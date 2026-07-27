export function DonutChart({ segments = [], size = 150, stroke = 20, dark, centerLabel, centerValue, legend = true, style }) {
  const palette = ['var(--accent-teal)', 'var(--brand-500)', 'var(--accent-purple)', 'var(--accent-coral)', 'var(--accent-orange)', 'var(--accent-green)'];
  const total = segments.reduce((s, x) => s + x.value, 0) || 1;
  const [m, setM] = React.useState(false);
  React.useEffect(() => { const r = requestAnimationFrame(() => setM(true)); return () => cancelAnimationFrame(r); }, []);

  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  let acc = 0;
  const textDim = dark ? 'var(--navy-text-dim)' : 'var(--ink-400)';
  const textFg = dark ? 'var(--navy-text)' : 'var(--ink-900)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 22, fontFamily: 'var(--font-sans)', ...style }}>
      <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {segments.map((s, i) => {
            const frac = s.value / total;
            const dash = (m ? frac : 0) * circ;
            const offset = -acc * circ;
            acc += frac;
            return (
              <circle key={i} cx={size / 2} cy={size / 2} r={r} fill="none"
                stroke={s.color || palette[i % palette.length]} strokeWidth={stroke}
                strokeDasharray={dash + ' ' + (circ - dash)} strokeDashoffset={offset}
                strokeLinecap="butt"
                style={{ transition: 'stroke-dasharray var(--dur-hero) var(--ease-out)' }} />
            );
          })}
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <span style={{ fontSize: size * 0.17, fontWeight: 800, color: textFg, letterSpacing: '-0.02em' }}>{centerValue}</span>
          {centerLabel && <span style={{ fontSize: size * 0.075, color: textDim, fontWeight: 600 }}>{centerLabel}</span>}
        </div>
      </div>
      {legend && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {segments.map((s, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: s.color || palette[i % palette.length] }} />
              <span style={{ color: textDim, minWidth: 56 }}>{s.label}</span>
              <span style={{ color: textFg, fontWeight: 700, marginLeft: 'auto' }}>{Math.round((s.value / total) * 100)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
