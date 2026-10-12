import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isGuestSession } from '../lib/auth'
import { useAppointments } from '../hooks/useAppointments'
import { useChat } from '../hooks/useChat'
import { useCurrentUser } from '../hooks/useCurrentUser'
import AppShell from '../components/app/AppShell'
import NavColumn from '../components/app/NavColumn'
import AppointmentsPanel from '../components/app/AppointmentsPanel'

const GREETING = 'Hi! I can help you book an appointment. What brings you in today?'
const GUEST_GREETING = 'Hi! This demo account already has two sample appointments. Try booking a new one, or ask me to reschedule or cancel one of them.'



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
      <div className="flex h-full">
        {appointmentsVisible && (
          <AppointmentsPanel
            appointments={appointments}
            showArchived={showArchived}
            onToggleArchived={toggleArchived}
            onArchive={archive}
          />
        )}
        <main className="flex min-w-0 flex-1 flex-col p-6">


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
    </div>
    </AppShell>
  )
}

export default Dashboard