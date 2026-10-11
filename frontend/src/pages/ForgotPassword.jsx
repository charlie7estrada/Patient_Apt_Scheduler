import { useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../lib/api'
import AuthLayout from '../components/auth/AuthLayout'
import WakeUpNote from '../components/auth/WakeUpNote'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import TextField from '../components/ui/TextField'

const ICON_PATH = 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z'

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await apiFetch(`/api/v1/auth/forgot-password`, {
        method: 'POST',
        body: JSON.stringify({ email })
      })

      if (!response.ok) {
        setError('Could not send a reset link. Please try again.')
        return
      }

      setSent(true)
    } catch {
      setError('Could not reach the server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      iconPath={ICON_PATH}
      title="Forgot your password?"
      subtitle="Enter your account email and we'll send you a reset link"
      footer={
        <>
          Remembered it?{' '}
          <Link to="/login" className="font-medium text-action hover:text-action-hover">Back to sign in</Link>
        </>
      }
    >
      {sent ? (
        <Alert tone="success">
          If an account exists for {email}, a reset link is on its way. It expires in 30 minutes.
        </Alert>
      ) : (
        <>
          {error && <Alert className="mb-4">{error}</Alert>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <TextField label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
            <Button type="submit" loading={loading} className="w-full">
              {loading ? 'Sending link…' : 'Send reset link'}
            </Button>
            {loading && <WakeUpNote />}
          </form>
        </>
      )}

      <p className="mt-4 text-center text-xs text-ink-muted">
        Email delivery isn't set up in this demo yet, so reset links only appear in the server log.
      </p>
    </AuthLayout>
  )
}

export default ForgotPassword
