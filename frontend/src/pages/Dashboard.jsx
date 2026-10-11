import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isGuestSession } from '../lib/auth'
import { useAppointments } from '../hooks/useAppointments'
import { useChat } from '../hooks/useChat'
import { useCurrentUser } from '../hooks/useCurrentUser'
import AppShell from '../components/app/AppShell'
import NavColumn from '../components/app/NavColumn'

const statusStyles = {
  pending: 'bg-amber-100 text-amber-700',
  confirmed: 'bg-teal-100 text-teal-700',
  cancelled: 'bg-red-100 text-red-700',
  completed: 'bg-slate-100 text-slate-600',
}
const PAST_STATUSES = ['completed', 'cancelled']
const GREETING = 'Hi! I can help you book an appointment. What brings you in today?'
const GUEST_GREETING = 'Hi! This demo account already has two sample appointments. Try booking a new one, or ask me to reschedule or cancel one of them.'

function sortAppointments(appointments) {
  const byTime = (a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at)
  const isPast = a => PAST_STATUSES.includes(a.status)

  return [
    ...appointments.filter(a => !isPast(a)).sort(byTime),
    ...appointments.filter(isPast).sort((a, b) => byTime(b, a)),
  ]
}

function Dashboard() {
  const [isGuest] = useState(isGuestSession)
  const [appointmentsVisible, setAppointmentsVisible] = useState(true)
  const navigate = useNavigate()
  const { fullName } = useCurrentUser()
  const { appointments, showArchived, toggleArchived, archive, refresh } = useAppointments()
  const { messages, input, setInput, loading, send } = useChat({
    greeting: isGuest ? GUEST_GREETING : GREETING,
    onReply: refresh,
  })

  function handleLogout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  function handleCreateAccount() {
    localStorage.removeItem('token')
    navigate('/register')
  }

  function handleSend(e) {
    e.preventDefault()
    send()
  }

    return (
    <AppShell
      isGuest={isGuest}
      onCreateAccount={handleCreateAccount}
      nav={
        <NavColumn
          fullName={fullName}
          isGuest={isGuest}
          appointmentsVisible={appointmentsVisible}
          onToggleAppointments={() => setAppointmentsVisible(v => !v)}
          onLogout={handleLogout}
        />
      }
    >
      <main className="mx-auto flex w-full max-w-5xl gap-6 p-6">
        {appointmentsVisible && (
          <aside className="w-72 shrink-0 bg-white rounded-2xl shadow-sm border border-slate-100 p-5 h-fit">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Your Appointments</h2>
            {appointments.length === 0 ? (
              <p className="text-sm text-slate-400 italic">No appointments booked yet.</p>
            ) : (
              <ul className="space-y-3">
                {sortAppointments(appointments).map(a => (
                  <li 
                    key={a.id} 
                    className={`relative border border-slate-100 bg-slate-50/50 rounded-xl p-3 ${
                      PAST_STATUSES.includes(a.status) ? 'opacity-60' : ''
                    }`}
                  >
                    {PAST_STATUSES.includes(a.status) && !a.is_archived && (
                      <button
                        onClick={() => archive(a.id)}
                        aria-label="Archive appointment"
                        title="Archive"
                        className="absolute top-2 right-2 w-5 h-5 flex items-center justify-center text-slate-300 hover:text-slate-600 transition"
                      >
                        &times;
                      </button>
                    )}
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
                    {a.is_archived && (
                      <span className="inline-block mt-2 ml-1.5 text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-400">
                        archived
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            )}
            <button
              onClick={toggleArchived}
              className="mt-4 text-xs text-slate-400 hover:text-slate-600 transition"
            >
              {showArchived ? 'Hide archived' : 'Show archived'}
            </button>
          </aside>
        )}

        <div className="flex-1 flex flex-col">
          <div className="flex-1 bg-white rounded-2xl shadow-sm border border-slate-100 p-4 mb-4 overflow-y-auto space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-sm px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-teal-600 text-white'
                    : msg.isError
                    ? 'bg-red-50 border border-red-200 text-red-700'
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
    </AppShell>
  )
}

export default Dashboard