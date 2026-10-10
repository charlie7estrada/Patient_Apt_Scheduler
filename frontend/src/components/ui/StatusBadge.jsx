const STATUS_STYLES = {
  confirmed: 'bg-action/10 text-action-hover',
  pending: 'bg-warning/10 text-warning-ink',
  cancelled: 'bg-danger/10 text-danger',
  completed: 'bg-subtle text-ink-muted',
}

function StatusBadge({ status }) {
  return (
    <span className={`inline-block rounded-lg px-2 py-0.5 text-xs font-medium capitalize ${STATUS_STYLES[status] ?? STATUS_STYLES.completed}`}>
      {status}
    </span>
  )
}

export default StatusBadge
