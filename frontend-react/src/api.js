export async function apiRequest(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = new Headers(options.headers)

  if (['POST', 'PATCH', 'DELETE'].includes(method)) {
    const tokenResponse = await fetch('/api/csrf-token', {
      credentials: 'include',
    })

    if (!tokenResponse.ok) {
      throw new Error('Unable to initialize request security')
    }

    const { csrf_token } = await tokenResponse.json()
    headers.set('X-CSRF-Token', csrf_token)
  }

  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`/api${path}`, {
    ...options,
    method,
    headers,
    credentials: 'include',
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || data.message || 'Request failed')
  }

  return data
}