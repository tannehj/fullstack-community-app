import { useEffect, useState } from 'react'
import { apiRequest } from './api.js'
import Login from './Login.jsx'


function Community() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [user, setUser] = useState(null)

  const [stories, setStories] = useState([])
  const [isLoadingStories, setIsLoadingStories] = useState(false)
  const [storiesError, setStoriesError] = useState('')

  useEffect(() => {
  let cancelled = false

  async function restoreSession() {
    try {
      const currentUser = await apiRequest('/current-user')

      if (!cancelled) {
        setUser(currentUser)
      }
    } catch {
      // Leave the login form visible if the session cannot be restored.
    }
  }

  restoreSession()

  return () => {
    cancelled = true
  }
}, [])

  useEffect(() => {
    if (!user) return

    let cancelled = false

    async function loadStories() {
      setIsLoadingStories(true)
      setStoriesError('')

      try {
        const data = await apiRequest('/stories')

        if (!cancelled) {
          setStories(data)
        }
      } catch (error) {
        if (!cancelled) {
          setStoriesError(error.message)
        }
      } finally {
        if (!cancelled) {
          setIsLoadingStories(false)
        }
      }
    }

    loadStories()

    return () => {
      cancelled = true
    }
  }, [user])
  return (
    <section>
      <h2>Community</h2>
      <p>Share your stories, experiences, and recommendations.</p>

          {user ? (
        <p>Welcome, {user.name}!</p>
       ) : (
        <Login onLogin={setUser} />
      )}

       {user && (
  <div>
    {isLoadingStories ? (
      <p role="status">Loading stories…</p>
    ) : storiesError ? (
      <p role="alert">{storiesError}</p>
    ) : stories.length === 0 ? (
      <p>No stories yet.</p>
    ) : (
      stories.map((story) => (
        <article key={story.id}>
          <h3>{story.name}</h3>
          <p>{story.story}</p>
          <small>
            {new Date(story.created_at).toLocaleString()}
          </small>
        </article>
      ))
    )}
  </div>
)}
      <button
  type="button"
  className="share-story-button"
  aria-expanded={isFormOpen}
  aria-controls="story-form"
  onClick={() => setIsFormOpen(!isFormOpen)}
>
  {isFormOpen ? 'Close form' : 'Share a story'}
</button>

{isFormOpen && (
  <form id="story-form" onSubmit={(event) => event.preventDefault()}>
    <label htmlFor="story-text">Your story</label>

    <textarea
      id="story-text"
      name="story"
      rows={5}
      maxLength={500}
      placeholder="Share an experience with your community…"
    />
  </form>
)}
    </section>
  )
}

export default Community