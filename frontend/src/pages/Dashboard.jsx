import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../lib/api'

const statusStyles = {
  pending: 'bg-amber-100 text-amber-700',
  confirmed: 'bg-teal-100 text-teal-700',
  cancelled: 'bg-red-100 text-red-700',
  completed: 'bg-slate-100 text-slate-600',
}

function Dashboard() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I can help you book an appointment. What brings you in today?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const [appointments, setAppointments] = useState([])

  async function fetchAppointments() {
    const response = await apiFetch('/api/v1/appointments/')
    if (!response) return
    const data = await response.json()
    setAppointments(data)
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchAppointments()
  }, [])

  function handleLogout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    const history = updatedMessages.slice(0, -1).map(m => ({
      role: m.role,
      content: m.content
    }))

    const response = await apiFetch('/api/v1/chat/', {
      method: 'POST',
      body: JSON.stringify({ text: input, history })
    })

    if (!response) return

    const data = await response.json()
    setMessages([...updatedMessages, { role: 'assistant', content: data.response }])
    fetchAppointments()
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-100 shadow-sm px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-teal-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-lg font-semibold text-slate-800">Patient Appointment Scheduler</h1>
        </div>
        <button
          onClick={handleLogout}
          className="text-sm text-slate-500 hover:text-red-600 transition"
        >
          Logout
        </button>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto p-6 flex gap-6">
        <aside className="w-72 shrink-0 bg-white rounded-2xl shadow-sm border border-slate-100 p-5 h-fit">
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Upcoming Appointments</h2>
          {appointments.length === 0 ? (
            <p className="text-sm text-slate-400 italic">No appointments booked yet.</p>
          ) : (
            <ul className="space-y-3">
              {appointments.map(a => (
                <li key={a.id} className="border border-slate-100 bg-slate-50/50 rounded-xl p-3">
                  <p className="text-sm font-medium text-slate-800">
                    {new Date(a.scheduled_at).toLocaleString([], { 
                      dateStyle: 'medium', 
                      timeStyle: 'short', 
                      timeZone: 'America/Chicago',
                      })} CT
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">{a.reason}</p>
                  <p className="text-xs text-slate-500">with {a.provider_name}</p>
                  <span className={`inline-block mt-2 text-xs px-2 py-0.5 rounded-full capitalize ${statusStyles[a.status] ?? 'bg-slate-100 text-slate-600'}`}>
                    {a.status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <div className="flex-1 flex flex-col">
          <div className="flex-1 bg-white rounded-2xl shadow-sm border border-slate-100 p-4 mb-4 overflow-y-auto space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-sm px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-teal-600 text-white'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-100 text-slate-500 px-4 py-2.5 rounded-2xl text-sm animate-pulse">Typing...</div>
              </div>
            )}
          </div>

          <form onSubmit={handleSend} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 border border-slate-200 rounded-lg px-3.5 py-2.5 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-teal-600 text-white font-medium px-5 py-2.5 rounded-lg shadow-sm hover:bg-teal-700 transition disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}

export default Dashboard