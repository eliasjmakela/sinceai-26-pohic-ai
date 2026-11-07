/** Renders paragraphs with **bold** only (the AI report format). No HTML injection: text is split, not parsed as HTML. */
export function Markdownish({ text }: { text: string }) {
  return (
    <div className="space-y-3 text-slate-800">
      {text.split(/\n\s*\n/).map((para, i) => (
        <p key={i}>
          {para.split(/(\*\*[^*]+\*\*)/).map((part, j) =>
            part.startsWith('**') ? <b key={j}>{part.slice(2, -2)}</b> : <span key={j}>{part}</span>,
          )}
        </p>
      ))}
    </div>
  )
}
