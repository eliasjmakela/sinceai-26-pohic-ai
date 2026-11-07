import { useEffect, useState } from 'react'
import { Beat0 } from './beats/Beat0'
import { Beat2 } from './beats/Beat2'
import { Beat3 } from './beats/Beat3'
import { Beat4 } from './beats/Beat4'
import { Beat6 } from './beats/Beat6'

// One screen per beat, deep-linkable as /#/beat-N (PRODUCT.md §4). Beats are added as they are built.
const BEATS: Record<number, () => React.JSX.Element> = { 0: Beat0, 2: Beat2, 3: Beat3, 4: Beat4, 6: Beat6 }

function beatFromHash(): number {
  const m = window.location.hash.match(/beat-(\d+)/)
  const n = m ? Number(m[1]) : 0
  return n in BEATS ? n : 0
}

export default function App() {
  const [beat, setBeat] = useState(beatFromHash)
  useEffect(() => {
    const onHash = () => setBeat(beatFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])
  const Beat = BEATS[beat]
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-amber-50 px-6 py-2 text-center text-xs text-amber-900">
        Synthetic data · hypothetical prices · simulation
      </div>
      <nav className="mx-auto flex max-w-6xl gap-2 px-6 pt-4 text-sm">
        {Object.keys(BEATS).map((n) => (
          <a key={n} href={`#/beat-${n}`} className={`rounded px-2 py-1 ${Number(n) === beat ? 'bg-slate-900 text-white' : 'text-slate-500'}`}>Beat {n}</a>
        ))}
      </nav>
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Beat />
      </main>
    </div>
  )
}
