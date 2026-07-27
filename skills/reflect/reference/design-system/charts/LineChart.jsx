export function LineChart({ data = [], labels = [], width = 480, height = 220, color = '#A78BFA', dark, yFormat, highlight, style }) {
  const pad = { l: 42, r: 14, t: 16, b: 26 };
  const w = width - pad.l - pad.r, h = height - pad.t - pad.b;
  const max = Math.max(...data) * 1.15 || 1;
  const pts = data.map((v, i) => [pad.l + (i / (data.length - 1)) * w, pad.t + h - (v / max) * h]);
  const line = pts.map((p, i) => (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
  const area = line + ' L' + pts[pts.length - 1][0].toFixed(1) + ' ' + (pad.t + h) + ' L' + pts[0][0].toFixed(1) + ' ' + (pad.t + h) + ' Z';
  const gid = React.useMemo(() => 'lc' + Math.random().toString(36).slice(2, 8), []);
  const gridColor = dark ? 'rgba(255,255,255,0.09)' : 'var(--ink-100)';
  const textColor = dark ? 'var(--navy-text-dim)' : 'var(--ink-400)';
  const fmt = yFormat || (v => v >= 1000 ? '$' + (v / 1000) + 'K' : '$' + v);
  const ticks = [0, 0.25, 0.5, 0.75, 1];
  const hi = highlight != null ? pts[highlight] : null;
  return (
    <svg width={width} height={height} viewBox={'0 0 ' + width + ' ' + height} preserveAspectRatio="xMidYMid meet" style={{ fontFamily: 'var(--font-sans)', display: 'block', maxWidth: '100%', ...style }}>
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      {ticks.map(t => {
        const y = pad.t + h - t * h;
        return (
          <g key={t}>
            <line x1={pad.l} x2={pad.l + w} y1={y} y2={y} stroke={gridColor} strokeDasharray="3 4" />
            <text x={pad.l - 8} y={y + 3.5} textAnchor="end" fontSize="10" fill={textColor}>{fmt(Math.round(max * t))}</text>
          </g>
        );
      })}
      <path d={area} fill={'url(#' + gid + ')'} />
      <path d={line} fill="none" stroke={color} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"
        style={{ strokeDasharray: 1400, strokeDashoffset: 1400, animation: 'sp-draw 1.3s var(--ease-out) forwards', '--draw-len': 1400 }} />
      {labels.map((l, i) => {
        const x = pad.l + (i / (labels.length - 1)) * w;
        return <text key={i} x={x} y={height - 8} textAnchor="middle" fontSize="10" fill={textColor}>{l}</text>;
      })}
      {hi && (
        <g>
          <line x1={hi[0]} x2={hi[0]} y1={pad.t} y2={pad.t + h} stroke={dark ? 'rgba(255,255,255,0.25)' : 'var(--ink-200)'} strokeDasharray="3 4" />
          <circle cx={hi[0]} cy={hi[1]} r="5" fill="#fff" stroke={color} strokeWidth="3" />
          <g transform={'translate(' + (hi[0] - 32) + ',' + (hi[1] - 38) + ')'}>
            <rect width="64" height="26" rx="8" fill="#fff" style={{ filter: 'drop-shadow(0 3px 8px rgba(28,32,84,0.25))' }} />
            <text x="32" y="17" textAnchor="middle" fontSize="11" fontWeight="700" fill="var(--ink-900)">{fmt(data[highlight])}</text>
          </g>
        </g>
      )}
    </svg>
  );
}
