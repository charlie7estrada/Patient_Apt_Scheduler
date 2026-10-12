// Sorting, grouping, and formatting for the appointments list. No markup here.
const CLINIC_TZ = 'America/Chicago'
const PAST_STATUSES = ['completed', 'cancelled']

export function isPast(appointment) {
  return PAST_STATUSES.includes(appointment.status)
}

const byTime = (a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at)

// Upcoming soonest first, past most recent first
export function splitAppointments(appointments) {
  return {
    upcoming: appointments.filter(a => !isPast(a)).sort(byTime),
    past: appointments.filter(isPast).sort((a, b) => byTime(b, a)),
  }
}

// Days are Central Time days, matching the times shown on the cards
function dayKey(iso) {
  return new Date(iso).toLocaleDateString('en-CA', { timeZone: CLINIC_TZ })
}

export function formatDay(iso) {
  return new Date(iso).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', timeZone: CLINIC_TZ })
}

export function formatTime(iso) {
  return `${new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', timeZone: CLINIC_TZ })} CT`
}

// Expects a sorted list; consecutive appointments on the same day share a group
export function groupByDay(appointments) {
  const groups = []
  for (const appointment of appointments) {
    const key = dayKey(appointment.scheduled_at)
    const last = groups[groups.length - 1]
    if (last && last.key === key) {
      last.items.push(appointment)
    } else {
      groups.push({ key, label: formatDay(appointment.scheduled_at), items: [appointment] })
    }
  }
  return groups
}
