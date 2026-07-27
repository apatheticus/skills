export function AnimatedCounter({ value = 0, duration = 1200, prefix = '', suffix = '', decimals = 0, style }) {
  const [display, setDisplay] = React.useState(0);
  React.useEffect(() => {
    let raf, start;
    const from = display;
    const step = ts => {
      if (!start) start = ts;
      const t = Math.min(1, (ts - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(from + (value - from) * eased);
      if (t < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  const formatted = display.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  return (
    <span style={{ fontFamily: 'var(--font-sans)', fontWeight: 800, letterSpacing: '-0.02em', fontVariantNumeric: 'tabular-nums', ...style }}>
      {prefix}{formatted}{suffix}
    </span>
  );
}
