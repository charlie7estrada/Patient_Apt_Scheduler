import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { apiFetch } from '../lib/api'
import AuthLayout from '../components/auth/AuthLayout'
import WakeUpNote from '../components/auth/WakeUpNote'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import TextField from '../components/ui/TextField'

const ICON_PATH = 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [guestLoading, setGuestLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await apiFetch(`/api/v1/auth/login`, {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Login failed')
        return
      }

      localStorage.setItem('token', data.access_token)
      navigate('/dashboard')
    } catch {
      setError('Could not reach the server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleGuestLogin() {
    setError('')
    setGuestLoading(true)

    try {
      const response = await apiFetch(`/api/v1/auth/guest`, {
        method: 'POST'
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Could not start the demo')
        return
      }

      localStorage.setItem('token', data.access_token)
      navigate('/dashboard')
    } catch {
      setError('Could not reach the server. Please try again.')
    } finally {
      setGuestLoading(false)
    }
  }

  return (
    <AuthLayout
      iconPath={ICON_PATH}
      title="Welcome back"
      subtitle="Sign in to manage your appointments"
      footer={
        <>
          Don't have an account?{' '}
          <Link to="/register" className="font-medium text-action hover:text-action-hover">Register</Link>
        </>
      }
    >
      {error && <Alert className="mb-4">{error}</Alert>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <TextField label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        <div>
          <TextField label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          <div className="mt-1 text-right">
            <Link to="/forgot-password" className="text-sm font-medium text-action hover:text-action-hover">Forgot password?</Link>
          </div>
        </div>
        <Button type="submit" loading={loading} disabled={guestLoading} className="w-full">
          {loading ? 'Signing in…' : 'Sign In'}
        </Button>
        {loading && <WakeUpNote />}
      </form>

      <div className="my-6 flex items-center gap-3">
        <div className="h-px flex-1 bg-line" />
        <span className="text-xs uppercase tracking-wide text-ink-muted">or</span>
        <div className="h-px flex-1 bg-line" />
      </div>

      <Button variant="secondary" onClick={handleGuestLogin} loading={guestLoading} disabled={loading} className="w-full">
        {guestLoading ? 'Starting demo…' : 'Try the demo'}
      </Button>
      {guestLoading ? (
        <WakeUpNote />
      ) : (
        <p className="mt-2 text-center text-xs text-ink-muted">No account needed. Demo data is deleted after 24 hours.</p>
      )}
    </AuthLayout>
  )
}

export default Login