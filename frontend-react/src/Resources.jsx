import { useState } from 'react'
import { apiRequest } from './api.js'

function Resources() {
  const [sourceUrl, setSourceUrl] = useState('')
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  const [source, setSource] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isReaderOpen, setIsReaderOpen] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setStatus('')
    setSource(null)
    setIsReaderOpen(false)

    try {
      const url = new URL(sourceUrl.trim())

      if (url.protocol !== 'https:') {
        throw new Error('Unsupported URL')
      }

      setSourceUrl(url.href)
    } catch {
      setError('Enter a complete HTTPS document or article link.')
      return
    }

    setIsLoading(true)
    try {
      const result = await apiRequest('/resources/source', {
        method: 'POST',
        body: JSON.stringify({ url: sourceUrl.trim() }),
      })
      setSource(result)
      setStatus('Source loaded. Open the reader below to read the extracted text.')
    } catch (error) {
      setError(error instanceof TypeError ? 'Unable to reach the server. Check that Flask is running.' : error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section aria-labelledby="resources-heading">
      <h2 id="resources-heading">Resources</h2>
      <p>
        Break down complex documents into simpler English.
      </p>

      <form className="resource-form" onSubmit={handleSubmit} noValidate>
        <label htmlFor="resource-url">Document or article link</label>
        <p id="resource-help">
          Paste an HTTPS article link from USCIS, USA.gov, or IRS.gov. PDF and topic search support come later.
        </p>
        <div className="resource-input-row">
          <input
            id="resource-url"
            type="url"
            inputMode="url"
            placeholder="https://www.uscis.gov/..."
            value={sourceUrl}
            onChange={(event) => {
              setSourceUrl(event.target.value)
              setError('')
              setStatus('')
            }}
            aria-describedby="resource-help resource-availability"
            aria-invalid={Boolean(error)}
            disabled={isLoading}
            required
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Loading source…' : 'Load source'}
          </button>
        </div>
        <p id="resource-availability" className="resource-note">
          Read the source inside the app. AI summaries are the next step.
        </p>
        {error && <p className="resource-error" role="alert">{error}</p>}
        {status && <p role="status">{status}</p>}
      </form>

      {isLoading && <p role="status">Retrieving the official source…</p>}
      {source && (
        <article className="resource-source">
          <h3>{source.title}</h3>
          <a href={source.url} target="_blank" rel="noopener noreferrer">
            Open original website ↗
          </a>
          <p>Retrieved: {new Date(source.retrieved_at).toLocaleString()}</p>
          <button
            type="button"
            className="share-story-button"
            aria-expanded={isReaderOpen}
            aria-controls="resource-reader"
            onClick={() => setIsReaderOpen(!isReaderOpen)}
          >
            {isReaderOpen ? 'Close reader' : 'Read inside the app'}
          </button>
          {isReaderOpen && (
            <div id="resource-reader" className="resource-reader">
              <p>Extracted source text · Original formatting may differ.</p>
              {source.text.split('\n\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
          )}
        </article>
      )}
    </section>
  )
}

export default Resources
