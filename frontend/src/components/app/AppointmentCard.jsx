import StatusBadge from '../ui/StatusBadge'
import { formatTime, isPast } from '../../lib/appointments'

function AppointmentCard({ appointment, onArchive }) {
  const canArchive = isPast(appointment) && !appointment.is_archived

  return (
    <li className="relative rounded-lg border border-line bg-surface p-3">
      {canArchive && (
        <button
          type="button"
          onClick={() => onArchive(appointment.id)}
          aria-label="Archive appointment"
          title="Archive"
          className="absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded text-ink-muted transition hover:bg-subtle hover:text-ink"
        >
          &times;
        </button>
      )}
      <p className="text-sm font-medium text-ink">{formatTime(appointment.scheduled_at)}</p>
      <p className="mt-0.5 text-sm text-ink">{appointment.reason}</p>
      <p className="text-xs text-ink-muted">with {appointment.provider_name}</p>
      <div className="mt-2 flex gap-1.5">
        <StatusBadge status={appointment.status} />
        {appointment.is_archived && (
          <span className="inline-block rounded-lg bg-subtle px-2 py-0.5 text-xs font-medium text-ink-muted">Archived</span>
        )}
      </div>
    </li>
  )
}

export default AppointmentCard
