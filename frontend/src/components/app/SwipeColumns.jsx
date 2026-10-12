import { useEffect, useRef, useState } from 'react'

// Below md, columns sit in a horizontal scroller that snaps to each one. Each is 85% wide
// so the next one peeks in. From md up the wrappers use display: contents, which removes
// them from layout, so the columns sit in a normal row.
function SwipeColumns({ columns }) {
  const scrollerRef = useRef(null)
  const [active, setActive] = useState(0)
  const swipeable = columns.length > 1

  // The column that is at least 60% visible is the one being viewed
  useEffect(() => {
    const scroller = scrollerRef.current
    if (!scroller || columns.length < 2) return

    const wrappers = Array.from(scroller.children)
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) setActive(wrappers.indexOf(entry.target))
      }
    }, { root: scroller, threshold: 0.6 })

    wrappers.forEach(wrapper => observer.observe(wrapper))
    return () => observer.disconnect()
  }, [columns.length])

  return (
    <div className="flex h-full flex-col">
      <div
        ref={scrollerRef}
        className="flex min-h-0 flex-1 snap-x snap-mandatory overflow-x-auto md:snap-none md:overflow-x-visible"
      >
        {columns.map(column => (
          <div key={column.key} className={`flex shrink-0 snap-start md:contents ${swipeable ? 'w-[85%]' : 'w-full'}`}>
            {column.content}
          </div>
        ))}
      </div>

      {swipeable && (
        <div className="flex justify-center gap-4 border-t border-line bg-surface py-2 text-xs md:hidden" aria-hidden="true">
          {columns.map((column, i) => (
            <span key={column.key} className={i === active ? 'font-semibold text-ink' : 'text-ink-muted'}>
              {column.label}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

export default SwipeColumns
