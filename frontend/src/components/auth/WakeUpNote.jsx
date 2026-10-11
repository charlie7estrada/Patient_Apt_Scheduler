// The backend sleeps on Render's free tier, so the first request after idle can be slow
function WakeUpNote() {
  return (
    <p className="mt-3 text-center text-xs text-ink-muted">
      This can take up to a minute if the server is waking up from idle.
    </p>
  )
}

export default WakeUpNote
