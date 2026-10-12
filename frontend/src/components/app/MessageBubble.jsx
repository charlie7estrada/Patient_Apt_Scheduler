const STYLES = {
  user: 'bg-action text-white',
  assistant: 'bg-subtle text-ink',
  error: 'border border-danger/20 bg-danger/5 text-danger',
}

function MessageBubble({ role, isError, children }) {
  const style = role === 'user' ? STYLES.user : isError ? STYLES.error : STYLES.assistant

  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
      {/* pre-wrap keeps the line breaks the assistant puts in longer replies */}
      <div className={`max-w-[75%] whitespace-pre-wrap rounded-xl px-4 py-2.5 text-sm leading-relaxed ${style}`}>
        {children}
      </div>
    </div>
  )
}

export default MessageBubble
