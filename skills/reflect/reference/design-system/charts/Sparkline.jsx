export function Sparkline({ data = [], width = 140, height = 40, color = 'var(--success)', fill = true, animate = true, style }) {
  if (!data.length) return null;
  const min = Math.min(...data), max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => [
    (i / (data.length - 1)) * (width - 4) + 2,
    height - 3 - ((v - min) / range) * (height - 6),
  ]);
  const path = pts.map((p, i) => (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
  const area = path + ' L' + pts[pts.length - 1][0].toFixed(1) + ' ' + height + ' L' + pts[0][0].toFixed(1) + ' ' + height + ' Z';
  const id = React.useMemo(() => 'sp' + Math.random().toString(36).slice(2, 8), []);
  return (
    <svg width={width} height={height} viewBox={'0 0 ' + width + ' ' + height} preserveAspectRatio="xMidYMid meet" style={{ display: 'block', maxWidth: '100%', ...style }}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.28" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {fill && <path d={area} fill={'url(#' + id + ')'} />}
      <path d={path} fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
        style={animate ? { strokeDasharray: 600, strokeDashoffset: 600, animation: 'sp-draw 1.1s var(--ease-out) forwards', '--draw-len': 600 } : undefined} />
      <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r="3.2" fill={color} stroke="#fff" strokeWidth="1.5" />
    </svg>
  );
}
