export function BarChart({ data = [], labels = [], width = 420, height = 200, color = 'var(--blue-500)', dark, rounded = 4, highlightMax = true, style }) {
  const pad = { l: 10, r: 10, t: 12, b: 24 };
  const w = width - pad.l - pad.r, h = height - pad.t - pad.b;
  const max = Math.max(...data) || 1;
  const bw = Math.min(26, (w / data.length) * 0.55);
  const maxIdx = data.indexOf(Math.max(...data));
  const textColor = dark ? 'var(--navy-text-dim)' : 'var(--ink-400)';
  return (
    <svg width={width} height={height} viewBox={'0 0 ' + width + ' ' + height} preserveAspectRatio="xMidYMid meet" style={{ fontFamily: 'var(--font-sans)', display: 'block', maxWidth: '100%', ...style }}>
      {data.map((v, i) => {
        const x = pad.l + (i + 0.5) * (w / data.length) - bw / 2;
        const bh = (v / max) * h;
        const isMax = highlightMax && i === maxIdx;
        return (
          <g key={i}>
            <rect x={x} y={pad.t + h - bh} width={bw} height={bh} rx={rounded}
              fill={isMax ? 'var(--brand-500)' : color} opacity={isMax ? 1 : 0.75}
              style={{ transformOrigin: x + 'px ' + (pad.t + h) + 'px', animation: 'sp-bar-grow 0.7s var(--ease-out) ' + i * 0.05 + 's both' }} />
            {labels[i] && <text x={x + bw / 2} y={height - 6} textAnchor="middle" fontSize="10" fill={textColor}>{labels[i]}</text>}
          </g>
        );
      })}
    </svg>
  );
}
