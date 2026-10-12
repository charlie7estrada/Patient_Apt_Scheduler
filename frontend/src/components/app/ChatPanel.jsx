import { useEffect, useRef } from 'react'
import ChatComposer from './ChatComposer'
import MessageBubble from './MessageBubble'

function ChatPanel({ messages, loading, input, onInputChange, onSend }) {
  const threadRef = useRef(null)

  // Keep the newest message in view. Scrolling the thread itself (rather than
  // scrollIntoView) avoids also scrolling the page around it.
  useEffect(() => {
    const thread = threadRef.current
    if (thread) thread.scrollTop = thread.scrollHeight
  }, [messages, loading])

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <div ref={threadRef} className="min-h-0 flex-1 space-y-4 overflow-y-auto rounded-xl border border-line bg-surface p-4">
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} isError={msg.isError}>
            {msg.content}
          </MessageBubble>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="animate-pulse rounded-xl bg-subtle px-4 py-2.5 text-sm text-ink-muted">Typing...</div>
          </div>
        )}
      </div>

      <ChatComposer value={input} onChange={onInputChange} onSend={onSend} disabled={loading} />
    </div>
  )
}

export default ChatPanel
