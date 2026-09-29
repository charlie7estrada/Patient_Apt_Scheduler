import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

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
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
        <p className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-3 py-2">
          This reset link is invalid or has expired.{' '}
          <Link to="/forgot-password" className="font-medium underline">Request a new link</Link>
        </p>
      )
    }

    if (done) {
      return (
        <p className="bg-teal-50 border border-teal-200 text-teal-700 text-sm rounded-lg px-3 py-2">
          Your password has been updated.{' '}
          <Link to="/login" className="font-medium underline">Sign in</Link>
        </p>
      )
    }

    return (
      <>
        {error && (
          <p className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-3 py-2 mb-4">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">New password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Confirm new password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-teal-600 text-white font-medium py-2.5 rounded-lg shadow-sm hover:bg-teal-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading && (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
            )}
            {loading ? 'Updating password…' : 'Update password'}
          </button>
          {loading && (
            <p className="text-xs text-slate-400 mt-3 text-center">
              This can take up to a minute if the server is waking up from idle.
            </p>
          )}
        </form>
      </>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-sky-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 md:p-10 rounded-2xl shadow-xl border border-slate-100 w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-slate-800">Choose a new password</h1>
          <p className="text-sm text-slate-500 mt-1 text-center">Reset links expire 30 minutes after they're requested</p>
        </div>

        {renderBody()}

        <p className="text-sm text-slate-500 mt-6 text-center">
          <Link to="/login" className="text-teal-600 hover:text-teal-700 font-medium">Back to sign in</Link>
        </p>
      </div>
    </div>
  )
}

export default ResetPassword
