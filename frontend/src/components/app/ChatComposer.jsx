import Button from '../ui/Button'

function ChatComposer({ value, onChange, onSend, disabled }) {
  function handleSubmit(e) {
    e.preventDefault()
    onSend()
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      {/* no visible label in a chat box, so aria-label names the field for screen readers */}
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder="Type a message..."
        aria-label="Message"
        className="min-w-0 flex-1 rounded-lg border border-line bg-surface px-3.5 py-2.5 text-ink placeholder:text-ink-muted/60 transition focus:border-action focus:outline-none focus:ring-2 focus:ring-action/30"
      />
      <Button type="submit" disabled={disabled}>Send</Button>
    </form>
  )
}

export default ChatComposer
