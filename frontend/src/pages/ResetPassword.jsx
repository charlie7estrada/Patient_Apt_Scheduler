import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { apiFetch } from '../lib/api'
import AuthLayout from '../components/auth/AuthLayout'
import WakeUpNote from '../components/auth/WakeUpNote'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import TextField from '../components/ui/TextField'

const ICON_PATH = 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z'

function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [linkRejected, setLinkRejected] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)

    try {
      const response = await apiFetch(`/api/v1/auth/reset-password`, {
        method: 'POST',
        body: JSON.stringify({ token, new_password: password })
      })

      if (response.status === 400) {
        setLinkRejected(true)
        return
      }

      if (!response.ok) {
        setError('Could not reset your password. Please try again.')
        return
      }

      setDone(true)
    } catch {
      setError('Could not reach the server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  function renderBody() {
    if (!token || linkRejected) {
      return (
        <Alert>
          This reset link is invalid or has expired.{' '}
          <Link to="/forgot-password" className="font-medium underline">Request a new link</Link>
        </Alert>
      )
    }

    if (done) {
      return (
        <Alert tone="success">
          Your password has been updated.{' '}
          <Link to="/login" className="font-medium underline">Sign in</Link>
        </Alert>
      )
    }

    return (
      <>
        {error && <Alert className="mb-4">{error}</Alert>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <TextField label="New password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          <TextField label="Confirm new password" type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
          <Button type="submit" loading={loading} className="w-full">
            {loading ? 'Updating password…' : 'Update password'}
          </Button>
          {loading && <WakeUpNote />}
        </form>
      </>
    )
  }

  return (
    <AuthLayout
      iconPath={ICON_PATH}
      title="Choose a new password"
      subtitle="Reset links expire 30 minutes after they're requested"
      footer={<Link to="/login" className="font-medium text-action hover:text-action-hover">Back to sign in</Link>}
    >
      {renderBody()}
    </AuthLayout>
  )
}

export default ResetPassword
