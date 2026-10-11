import { useEffect, useState } from 'react'
import { apiFetch } from '../lib/api'

export function useCurrentUser() {
  const [fullName, setFullName] = useState(null)

  useEffect(() => {
    let ignore = false

    async function load() {
      try {
        const response = await apiFetch('/api/v1/auth/me')
        if (!response || !response.ok) return
        const data = await response.json()
        if (!ignore) setFullName(data.full_name)
      } catch {
        // the name is only shown in the nav; leave it empty rather than block the page
      }
    }

    load()
    // a response that arrives after the component unmounts shouldn't set state
    return () => { ignore = true }
  }, [])

  return { fullName }
}
