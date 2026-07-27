export function SegmentGauge({ value = 0, max = 100, size = 150, segments = 28, label, unit = '%', color = 'var(--brand-500)', style }) {
  const [m, setM] = React.useState(false);
  React.useEffect(() => { const r = requestAnimationFrame(() => setM(true)); return () => cancelAnimationFrame(r); }, []);
  const pct = Math.min(1, value / max);
  const cx = size / 2, cy = size / 2;
  const rOuter = size / 2 - 4, rInner = size / 2 - 17;
  const startAngle = 225, sweep = 270; // gap at bottom (speedometer) — tips at ±135° from top
  // lowest tick tips → y = cy + rOuter·cos45° (+ cap)
  const contentH = Math.ceil(cy + rOuter * Math.SQRT1_2 + 5);
  const polar = (angle, r) => {
    const a = (angle - 90) * Math.PI / 180;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  };
  const numSize = Math.max(18, size * 0.19);
  const unitSize = Math.max(11, size * 0.1);
  const labelSize = Math.max(10, size * 0.075);
  return (
    <div style={{ position: 'relative', width: size, height: contentH, maxWidth: '100%', fontFamily: 'var(--font-sans)', ...style }}>
      <svg width={size} height={contentH} viewBox={'0 0 ' + size + ' ' + contentH} preserveAspectRatio="xMidYMid meet" style={{ display: 'block' }}>
        {Array.from({ length: segments }).map((_, i) => {
          const frac = i / (segments - 1);
          const angle = startAngle + frac * sweep;
          const [x1, y1] = polar(angle, rInner);
          const [x2, y2] = polar(angle, rOuter);
          const on = m && frac <= pct;
          return (
            <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
              stroke={on ? color : 'var(--ink-100)'} strokeWidth={3.5} strokeLinecap="round"
              style={{ transition: 'stroke var(--dur-fast) var(--ease-out) ' + (i * 22) + 'ms' }} />
          );
        })}
      </svg>
      <div style={{ position: 'absolute', left: 0, right: 0, top: cy, textAlign: 'center', transform: 'translateY(-50%)' }}>
        <div style={{ fontSize: numSize, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.02em', lineHeight: 1 }}>{Math.round(pct * 100)}<span style={{ fontSize: unitSize, fontWeight: 700, color: 'var(--ink-400)' }}>{unit}</span></div>
        {label && <div style={{ fontSize: labelSize, color: 'var(--ink-400)', fontWeight: 600, marginTop: 3, lineHeight: 1.2 }}>{label}</div>}
      </div>
    </div>
  );
}
