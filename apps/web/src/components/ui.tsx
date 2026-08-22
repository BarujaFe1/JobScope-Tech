export function DemoBanner({ source }: { source: "api" | "demo" }) {
  if (source === "api") {
    return null;
  }
  return (
    <div
      role="status"
      className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950"
    >
      <strong className="font-semibold">Modo demo.</strong> A API local não respondeu — exibindo
      snapshot embutido. Suba o backend em <code className="font-mono text-xs">:8000</code> para
      dados ao vivo.
    </div>
  );
}

export function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
      <p className="text-xs font-medium uppercase tracking-[0.14em] text-[var(--muted)]">{label}</p>
      <p className="mt-2 font-display text-3xl font-semibold tracking-tight text-[var(--ink)]">
        {value}
      </p>
      {hint ? <p className="mt-2 text-sm text-[var(--muted)]">{hint}</p> : null}
    </div>
  );
}

export function DistributionBars({
  title,
  data,
  labelFn,
}: {
  title: string;
  data: Record<string, number>;
  labelFn?: (key: string) => string;
}) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(...entries.map(([, n]) => n), 1);
  return (
    <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
      <h2 className="font-display text-lg font-semibold text-[var(--ink)]">{title}</h2>
      <ul className="mt-4 space-y-3">
        {entries.map(([key, count]) => (
          <li key={key}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-[var(--ink)]">{labelFn ? labelFn(key) : key}</span>
              <span className="tabular-nums text-[var(--muted)]">{count}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-[var(--surface-2)]">
              <div
                className="h-full rounded-full bg-[var(--accent)] transition-all duration-700"
                style={{ width: `${(count / max) * 100}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-xl border border-dashed border-[var(--line)] bg-[var(--surface)] px-6 py-12 text-center">
      <p className="font-display text-lg font-semibold text-[var(--ink)]">{title}</p>
      <p className="mx-auto mt-2 max-w-md text-sm text-[var(--muted)]">{body}</p>
    </div>
  );
}
