import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isGuestSession } from '../lib/auth'
import { useAppointments } from '../hooks/useAppointments'
import { useChat } from '../hooks/useChat'
import { useCurrentUser } from '../hooks/useCurrentUser'
import AppShell from '../components/app/AppShell'
import NavColumn from '../components/app/NavColumn'
import AppointmentsPanel from '../components/app/AppointmentsPanel'
import ChatPanel from '../components/app/ChatPanel'

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
                <main className="flex min-w-0 flex-1 flex-col p-4 md:p-6">
          <ChatPanel
            messages={messages}
            loading={loading}
            input={input}
            onInputChange={setInput}
            onSend={send}
          />
      </main>
    </div>
    </AppShell>
  )
}

export default Dashboard