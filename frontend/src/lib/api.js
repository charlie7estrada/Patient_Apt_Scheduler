const API_URL = import.meta.env.VITE_API_URL

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('token')

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    }
  })

  // Only a request that carried a session can have that session rejected. A 401 without
  // a token is an ordinary error, like a wrong password on the login page.
  if (response.status === 401 && token) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    return
  }

  return response
}