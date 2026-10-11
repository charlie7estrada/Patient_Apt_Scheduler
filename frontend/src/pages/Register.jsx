import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { apiFetch } from '../lib/api'
import AuthLayout from '../components/auth/AuthLayout'
import WakeUpNote from '../components/auth/WakeUpNote'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import TextField from '../components/ui/TextField'

const ICON_PATH = 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a3 3 0 11-6 0 3 3 0 016 0zM3 20a6 6 0 0112 0v1H3v-1z'

function Register() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'patient'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await apiFetch(`/api/v1/auth/register`, {
        method: 'POST',
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Registration failed')
        return
      }

      navigate('/login')
    } catch {
      setError('Could not reach the server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      iconPath={ICON_PATH}
      title="Create your account"
      subtitle="Get started booking appointments"
      footer={
        <>
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-action hover:text-action-hover">Sign in</Link>
        </>
      }
    >
      {error && <Alert className="mb-4">{error}</Alert>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <TextField label="Full Name" name="full_name" value={formData.full_name} onChange={handleChange} required />
        <TextField label="Email" type="email" name="email" value={formData.email} onChange={handleChange} required />
        <TextField label="Password" type="password" name="password" value={formData.password} onChange={handleChange} required />
        <div>
          <label htmlFor="role" className="mb-1 block text-sm font-medium text-ink-muted">I am a</label>
          <select
            id="role"
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-ink transition focus:border-action focus:outline-none focus:ring-2 focus:ring-action/30"
          >
            <option value="patient">Patient</option>
            <option value="provider">Provider</option>
          </select>
        </div>
        <Button type="submit" loading={loading} className="w-full">
          {loading ? 'Creating account…' : 'Create Account'}
        </Button>
        {loading && <WakeUpNote />}
      </form>
    </AuthLayout>
  )
}

export default Register