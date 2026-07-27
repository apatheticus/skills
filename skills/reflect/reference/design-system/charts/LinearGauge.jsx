export function LinearGauge({ value = 0, max = 100, label, unit = '%', height = 10,
  zones = [ { to: 50, color: 'var(--danger)' }, { to: 80, color: 'var(--warning)' }, { to: 100, color: 'var(--success)' } ], style }) {
  const [m, setM] = React.useState(false);
  React.useEffect(() => { const r = requestAnimationFrame(() => setM(true)); return () => cancelAnimationFrame(r); }, []);
  const pct = Math.min(100, (value / max) * 100);
  const shown = m ? pct : 0;
  let from = 0;
  const zone = zones.find(z => pct <= z.to) || zones[zones.length - 1];
  return (
    <div style={{ fontFamily: 'var(--font-sans)', ...style }}>
      {(label || unit) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          {label && <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--ink-600)' }}>{label}</span>}
          <span style={{ fontSize: 12, fontWeight: 700, color: zone.color, fontFamily: 'var(--font-mono)' }}>{Math.round(pct)}{unit}</span>
        </div>
      )}
      <div style={{ position: 'relative', paddingTop: 8 }}>
        <div style={{ display: 'flex', height, borderRadius: 999, overflow: 'hidden', gap: 2 }}>
          {zones.map((z, i) => {
            const w = z.to - from; from = z.to;
            return <div key={i} style={{ width: w + '%', background: z.color, opacity: 0.22 }} />;
          })}
        </div>
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: 'calc(' + shown + '% - 1.5px)',
          transition: 'left var(--dur-hero) var(--ease-out)', pointerEvents: 'none' }}>
          <div style={{ width: 3, height: '100%', borderRadius: 999, background: zone.color,
            boxShadow: '0 0 0 2px #fff, 0 2px 6px rgba(28,32,84,0.3)', transition: 'background var(--dur-base) var(--ease-out)' }} />
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5, fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--ink-400)' }}>
        <span>0</span><span>{max}{unit === '%' ? '' : unit}</span>
      </div>
    </div>
  );
}
