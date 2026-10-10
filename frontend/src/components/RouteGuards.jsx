import { Navigate } from 'react-router-dom'
import { hasValidSession } from '../lib/auth'

export function ProtectedRoute({ children }) {
  return hasValidSession() ? children : <Navigate to="/login" replace />
}

export function GuestRoute({ children }) {
  return hasValidSession() ? <Navigate to="/dashboard" replace /> : children
}
