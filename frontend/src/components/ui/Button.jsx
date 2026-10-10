const VARIANTS = {
  primary: 'bg-action text-white shadow-sm hover:bg-action-hover',
  secondary: 'border border-action text-action hover:bg-action/5',
  ghost: 'text-ink-muted hover:text-ink',
}

function Spinner() {
  return (
    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  )
}

// Defaults to type="button" so a button inside a form only submits when asked to
function Button({ variant = 'primary', loading = false, disabled, type = 'button', className = '', children, ...props }) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition disabled:opacity-50 ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {loading && <Spinner />}
      {children}
    </button>
  )
}

export default Button
