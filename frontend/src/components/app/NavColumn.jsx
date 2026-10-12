import Icon from '../ui/Icon'

function initials(name) {
  if (!name) return ''
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map(word => word[0].toUpperCase()).join('')
}

const ITEM = 'flex w-full items-center justify-center rounded-lg px-2 py-2 text-sm font-medium transition md:justify-start md:px-3'

// Full column from the md breakpoint up; below it, a narrow icon rail with the labels hidden.
// aria-label keeps the icon-only buttons readable to screen readers.
function NavColumn({ fullName, isGuest, appointmentsVisible, onToggleAppointments, onLogout }) {
  const toggleLabel = appointmentsVisible ? 'Hide appointments' : 'Show appointments'
  const logoutLabel = isGuest ? 'Exit demo' : 'Logout'

  return (
    <nav className="flex w-14 shrink-0 flex-col border-r border-line bg-surface p-2 md:w-60 md:p-3">
      <div className="mb-4 flex items-center justify-center gap-3 md:justify-start md:px-1">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand text-sm font-semibold text-white">
          {initials(fullName)}
        </div>
        <span className="hidden truncate text-sm font-medium text-ink md:block">{fullName}</span>
      </div>

      <button
        type="button"
        onClick={onToggleAppointments}
        aria-label={toggleLabel}
        aria-pressed={appointmentsVisible}
        className={`${ITEM} flex-col gap-1 md:flex-row md:gap-3 ${appointmentsVisible ? 'bg-select text-select-ink' : 'text-ink-muted hover:bg-subtle hover:text-ink'}`}
      >
        <Icon name="calendar" />
        <span className="hidden md:inline">{toggleLabel}</span>
        <Icon name={appointmentsVisible ? 'chevron-left' : 'chevron-right'} className="h-4 w-4 md:ml-auto" />
      </button>

      <button
        type="button"
        onClick={onLogout}
        aria-label={logoutLabel}
        className={`${ITEM} mt-auto gap-3 text-ink-muted hover:bg-subtle hover:text-ink`}
      >
        <Icon name="logout" />
        <span className="hidden md:inline">{logoutLabel}</span>
      </button>
    </nav>
  )
}

export default NavColumn
