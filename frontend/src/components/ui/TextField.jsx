import { useId } from 'react'

// useId links the label to its input, so clicking the label focuses the field
// and screen readers announce the label with it
function TextField({ label, className = '', ...props }) {
  const id = useId()

  return (
    <div className={className}>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-ink-muted">
        {label}
      </label>
      <input
        id={id}
        className="w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-ink placeholder:text-ink-muted/60 transition focus:border-action focus:outline-none focus:ring-2 focus:ring-action/30"
        {...props}
      />
    </div>
  )
}

export default TextField
