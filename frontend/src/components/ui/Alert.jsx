const TONES = {
  error: 'border-danger/20 bg-danger/5 text-danger',
  success: 'border-action/20 bg-action/5 text-action-hover',
  info: 'border-line bg-subtle text-ink-muted',
}

// role="alert" makes screen readers announce errors as soon as they appear
function Alert({ tone = 'error', className = '', children }) {
  return (
    <p
      role={tone === 'error' ? 'alert' : 'status'}
      className={`rounded-lg border px-3 py-2 text-sm ${TONES[tone]} ${className}`}
    >
      {children}
    </p>
  )
}

export default Alert
