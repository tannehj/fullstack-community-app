import { useState } from 'react'

function Resources() {
  const [sourceUrl, setSourceUrl] = useState('')
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setStatus('')

    try {
      const url = new URL(sourceUrl.trim())

      if (!['https:', 'http:'].includes(url.protocol)) {
        throw new Error('Unsupported URL')
      }

      setSourceUrl(url.href)
      setStatus('Link checked. AI summaries and the in-app reader are not connected yet.')
    } catch {
      setError('Enter a complete http:// or https:// document or article link.')
    }
  }

  return (
    <section aria-labelledby="resources-heading">
      <h2 id="resources-heading">Resources</h2>
      <p>
        Find documents and articles, understand them in simple language,
        and explore the original source.
      </p>

      <form className="resource-form" onSubmit={handleSubmit} noValidate>
        <label htmlFor="resource-url">Document or article link</label>
        <p id="resource-help">
          Paste a source link to get started. Topic search is coming later.
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
            required
          />
          <button type="submit">Summarize</button>
        </div>
        <p id="resource-availability" className="resource-note">
          Summarization is being connected. This form currently checks your link only.
        </p>
        {error && <p className="resource-error" role="alert">{error}</p>}
        {status && <p role="status">{status}</p>}
      </form>
    </section>
  )
}

export default Resources
