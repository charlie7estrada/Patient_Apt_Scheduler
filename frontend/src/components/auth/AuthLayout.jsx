// Shared frame for the signed-out pages. Each page supplies its icon, heading, form and footer link.
function AuthLayout({ iconPath, title, subtitle, footer, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-page p-4">
      <div className="w-full max-w-md rounded-xl border border-line bg-surface p-8 shadow-sm md:p-10">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-brand text-white">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" d={iconPath} />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-ink">{title}</h1>
          <p className="mt-1 text-sm text-ink-muted">{subtitle}</p>
        </div>

        {children}

        {footer && <p className="mt-6 text-center text-sm text-ink-muted">{footer}</p>}
      </div>
    </div>
  )
}

export default AuthLayout
