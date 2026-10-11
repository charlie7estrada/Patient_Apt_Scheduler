import Icon from '../ui/Icon'

// Header and demo banner stay fixed; only the content area scrolls
function AppShell({ nav, isGuest, onCreateAccount, children }) {
  return (
    <div className="flex h-dvh flex-col bg-page">
      <header className="flex items-center gap-3 border-b border-line bg-surface px-4 py-3 md:px-6">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand text-white">
          <Icon name="logo" />
        </div>
        <h1 className="truncate text-lg font-semibold text-ink">Patient Appointment Scheduler</h1>
      </header>

      {isGuest && (
        <div className="border-b border-line bg-soft px-4 py-2.5 text-center text-sm text-ink md:px-6">
          You're using a demo account. Anything you book is deleted after 24 hours.{' '}
          <button type="button" onClick={onCreateAccount} className="font-medium text-brand underline">
            Create a free account
          </button>
        </div>
      )}

      <div className="flex min-h-0 flex-1">
        {nav}
        <div className="min-w-0 flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  )
}

export default AppShell
