import { useState } from 'react'
import { apiFetch } from '../lib/api'

// onReply runs after every successful reply, so the caller can react to bookings
// (the Dashboard passes the appointments refresh)
export function useChat({ greeting, onReply }) {
  const [messages, setMessages] = useState([{ role: 'assistant', content: greeting }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  async function send() {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    const history = updatedMessages
      .slice(0, -1)
      .filter(m => !m.isError)
      .map(m => ({ role: m.role, content: m.content }))

    try {
      const response = await apiFetch('/api/v1/chat/', {
        method: 'POST',
        body: JSON.stringify({ text: input, history })
      })

      if (response) {
        const data = await response.json().catch(() => ({}))

        if (response.ok) {
          setMessages([...updatedMessages, { role: 'assistant', content: data.response }])
          onReply?.()
        } else {
          setMessages([...updatedMessages, {
            role: 'assistant',
            isError: true,
            content: data.detail || 'Something went wrong. Please try again.'
          }])
        }
      }
    } catch {
      setMessages([...updatedMessages, {
        role: 'assistant',
        isError: true,
        content: 'Could not reach the server. Please check your connection and try again.'
      }])
    }

    setLoading(false)
  }

  return { messages, input, setInput, loading, send }
}
