export function isGuestSession() {
  const token = localStorage.getItem('token')
  if (!token) return false

  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(payload)).guest === true
  } catch {
    return false
  }
}
