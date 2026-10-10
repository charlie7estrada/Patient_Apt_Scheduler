export function decodeToken(token) {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

// The backend still enforces expiry; this just avoids showing a page the session can't use.
// Expired or unreadable tokens are removed so they don't ride along on later requests.
export function hasValidSession() {
  const token = localStorage.getItem('token')
  if (!token) return false

  const claims = decodeToken(token)
  if (claims?.exp && claims.exp * 1000 > Date.now()) return true

  localStorage.removeItem('token')
  return false
}

export function isGuestSession() {
  const token = localStorage.getItem('token')
  return token ? decodeToken(token)?.guest === true : false
}
