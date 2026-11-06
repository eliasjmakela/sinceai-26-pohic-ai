import { useEffect, useState } from 'react'
import { Beat0 } from './beats/Beat0'

// One screen per beat, deep-linkable as /#/beat-N (PRODUCT.md §4). Beats are added as they are built.
const BEATS = [Beat0]

function beatFromHash(): number {
  const m = window.location.hash.match(/beat-(\d+)/)
  const n = m ? Number(m[1]) : 0
  return n >= 0 && n < BEATS.length ? n : 0
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
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Beat />
      </main>
    </div>
  )
}
