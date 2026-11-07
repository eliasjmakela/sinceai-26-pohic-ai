import { useEffect, useState } from 'react'
import { Business } from './details/Business'
import { Customer } from './details/Customer'
import { Fleet } from './details/Fleet'
import { Market } from './details/Market'
import { Operator } from './details/Operator'
import { Today } from './pitch/Today'
import { Value } from './pitch/Value'
import { Weight } from './pitch/Weight'

// Three pitch screens (PRODUCT.md §4), then detail screens for questions and the walkthrough. Deep links: /#/beat-1, /#/market.
type Screen = { id: string; label: string; view: () => React.JSX.Element }
const PITCH: Screen[] = [
  { id: 'beat-1', label: '1 · Today', view: Today },
  { id: 'beat-2', label: '2 · The weight', view: Weight },
  { id: 'beat-3', label: '3 · The value', view: Value },
]
const DETAILS: Screen[] = [
  { id: 'fleet', label: 'Fleet', view: Fleet },
  { id: 'customer', label: 'Customer', view: Customer },
  { id: 'operator', label: 'Operator', view: Operator },
  { id: 'market', label: 'Market', view: Market },
  { id: 'business', label: 'Business', view: Business },
]
const ALL = [...PITCH, ...DETAILS]

function screenFromHash(): Screen {
  const id = window.location.hash.replace(/^#\/?/, '')
  return ALL.find((s) => s.id === id) ?? PITCH[0]
}

export default function App() {
  const [screen, setScreen] = useState(screenFromHash)
  useEffect(() => {
    const onHash = () => { setScreen(screenFromHash()); window.scrollTo(0, 0) }
    // Arrow keys step through the pitch screens, so the presenter never types.
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return
      const i = PITCH.findIndex((s) => s.id === screenFromHash().id)
      if (i < 0) return
      const next = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : -1
      if (next >= 0 && next < PITCH.length) window.location.hash = `#/${PITCH[next].id}`
    }
    window.addEventListener('hashchange', onHash)
    window.addEventListener('keydown', onKey)
    return () => { window.removeEventListener('hashchange', onHash); window.removeEventListener('keydown', onKey) }
  }, [])
  const View = screen.view
  const link = (s: Screen) => (
    <a key={s.id} href={`#/${s.id}`} className={`rounded px-2 py-1 ${s.id === screen.id ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'}`}>{s.label}</a>
  )
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-amber-50 px-6 py-2 text-center text-xs text-amber-900">
        Synthetic data · hypothetical prices · simulation
      </div>
      <nav className="mx-auto flex max-w-6xl flex-wrap items-center gap-2 px-6 pt-4 text-sm">
        <span className="mr-2 font-bold text-teal-800">OpenWeight</span>
        {PITCH.map(link)}
        <span className="ml-auto mr-1 text-xs uppercase tracking-wide text-slate-400">details</span>
        {DETAILS.map(link)}
      </nav>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <View />
      </main>
    </div>
  )
}
