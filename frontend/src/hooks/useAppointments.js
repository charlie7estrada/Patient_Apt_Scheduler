import { useCallback, useEffect, useState } from 'react'
import { apiFetch } from '../lib/api'

export function useAppointments() {
  const [appointments, setAppointments] = useState([])
  const [showArchived, setShowArchived] = useState(false)
  // Bumping this re-runs the fetch effect; it's how refresh() asks for new data
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    let ignore = false

    async function load() {
      try {
        const response = await apiFetch(`/api/v1/appointments/?include_archived=${showArchived}`)
        if (!response || !response.ok) return
        const data = await response.json().catch(() => null)
        if (!ignore && Array.isArray(data)) setAppointments(data)
      } catch {
        // keep whatever list is already on screen; chat surfaces its own errors
      }
    }

    load()
    // if the archived toggle flips mid-request, drop the older response
    return () => { ignore = true }
  }, [showArchived, refreshKey])

  const refresh = useCallback(() => setRefreshKey(k => k + 1), [])

  async function archive(id) {
    try {
      const response = await apiFetch(`/api/v1/appointments/${id}/archive`, { method: 'POST' })
      if (!response || !response.ok) return
      refresh()
    } catch {
      // leave the list alone; the next refresh reconciles it
    }
  }

  function toggleArchived() {
    setShowArchived(v => !v)
  }

  return { appointments, showArchived, toggleArchived, archive, refresh }
}
