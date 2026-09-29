import { useState } from 'react'
import { Link } from 'react-router-dom'

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
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-sky-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 md:p-10 rounded-2xl shadow-xl border border-slate-100 w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-slate-800">Forgot your password?</h1>
          <p className="text-sm text-slate-500 mt-1 text-center">Enter your account email and we'll send you a reset link</p>
        </div>

        {sent ? (
          <p className="bg-teal-50 border border-teal-200 text-teal-700 text-sm rounded-lg px-3 py-2">
            If an account exists for {email}, a reset link is on its way. It expires in 30 minutes.
          </p>
        ) : (
          <>
            {error && (
              <p className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-3 py-2 mb-4">
                {error}
              </p>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
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
                {loading ? 'Sending link…' : 'Send reset link'}
              </button>
              {loading && (
                <p className="text-xs text-slate-400 mt-3 text-center">
                  This can take up to a minute if the server is waking up from idle.
                </p>
              )}
            </form>
          </>
        )}

        <p className="text-xs text-slate-400 mt-4 text-center">
          Email delivery isn't set up in this demo yet, so reset links only appear in the server log.
        </p>

        <p className="text-sm text-slate-500 mt-6 text-center">
          Remembered it?{' '}
          <Link to="/login" className="text-teal-600 hover:text-teal-700 font-medium">Back to sign in</Link>
        </p>
      </div>
    </div>
  )
}

export default ForgotPassword
