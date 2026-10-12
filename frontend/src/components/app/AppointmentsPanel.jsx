import AppointmentCard from './AppointmentCard'
import { groupByDay, splitAppointments } from '../../lib/appointments'

// One labeled section (Upcoming or Past), with appointments grouped under day headers
function Section({ title, appointments, onArchive }) {
  if (appointments.length === 0) return null

  return (
    <section className="space-y-3">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-muted">{title}</h3>
      {groupByDay(appointments).map(group => (
        <div key={group.key}>
          <p className="mb-1.5 text-xs text-ink-muted">{group.label}</p>
          <ul className="space-y-2">
            {group.items.map(appointment => (
              <AppointmentCard key={appointment.id} appointment={appointment} onArchive={onArchive} />
            ))}
          </ul>
        </div>
      ))}
    </section>
  )
}

function AppointmentsPanel({ appointments, showArchived, onToggleArchived, onArchive }) {
  const { upcoming, past } = splitAppointments(appointments)

  return (
    <aside className="flex w-full shrink-0 flex-col border-r border-line bg-surface md:w-72">
      <h2 className="px-4 pt-4 text-sm font-semibold text-ink">Your appointments</h2>

      <div className="flex-1 space-y-6 overflow-y-auto p-4">
        {appointments.length === 0 ? (
          <p className="text-sm text-ink-muted">No appointments booked yet.</p>
        ) : (
          <>
            <Section title="Upcoming" appointments={upcoming} onArchive={onArchive} />
            <Section title="Past" appointments={past} onArchive={onArchive} />
          </>
        )}
      </div>

      <div className="border-t border-line px-4 py-3">
        <button type="button" onClick={onToggleArchived} className="text-xs font-medium text-ink-muted transition hover:text-ink">
          {showArchived ? 'Hide archived' : 'Show archived'}
        </button>
      </div>
    </aside>
  )
}

export default AppointmentsPanel
