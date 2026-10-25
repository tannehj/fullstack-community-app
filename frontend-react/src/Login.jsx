import { useState } from 'react'
import { apiRequest } from './api.js'

function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function appLogin(event) {
    event.preventDefault()

    const usernameValue = username.trim()

    if (!usernameValue || !password) {
      setMessage('Username or password is missing.')
      return
    }

    setMessage('')
    setIsLoading(true)

    try {
      await apiRequest('/login', {
        method: 'POST',
        body: JSON.stringify({
          username: usernameValue,
          password,
        }),
      })

      const user = await apiRequest('/current-user')
      setPassword('')
      onLogin(user)
    } catch (error) {
      setMessage(
        error instanceof TypeError
          ? 'Unable to connect to the server. Please try again later.'
          : error.message
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form id="login-form" onSubmit={appLogin}>
      <h3>Log in</h3>

      <label htmlFor="username">Username</label>
      <input
        type="text"
        id="username"
        name="username"
        placeholder="Enter username"
        autoComplete="username"
        value={username}
        onChange={(event) => setUsername(event.target.value)}
        required
      />

      <label htmlFor="password">Password</label>
      <input
        type="password"
        id="password"
        name="password"
        placeholder="Enter password"
        autoComplete="current-password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        required
      />

      {message && <p role="alert">{message}</p>}

      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in…' : 'Log in'}
      </button>
    </form>
  )
}

export default Login