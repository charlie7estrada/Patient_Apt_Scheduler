import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    const data = await response.json()

    if (!response.ok) {
      setError(data.detail || 'Login failed')
      return
    }

    localStorage.setItem('token', data.access_token)
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-sky-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 md:p-10 rounded-2xl shadow-xl border border-slate-100 w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-slate-800">Welcome back</h1>
          <p className="text-sm text-slate-500 mt-1">Sign in to manage your appointments</p>
        </div>

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
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-teal-600 text-white font-medium py-2.5 rounded-lg shadow-sm hover:bg-teal-700 transition"
          >
            Sign In
          </button>
        </form>

        <p className="text-sm text-slate-500 mt-6 text-center">
          Don't have an account?{' '}
          <Link to="/register" className="text-teal-600 hover:text-teal-700 font-medium">Register</Link>
        </p>
      </div>
    </div>
  )
}

export default Login