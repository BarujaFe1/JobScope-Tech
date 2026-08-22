import Link from "next/link";

import { gapStatus, snapshot } from "@/lib/snapshot";

const TONE_CLASSES: Record<"demand" | "ok" | "muted", string> = {
  demand: "border-rose-200 bg-rose-50 text-rose-900",
  ok: "border-teal-200 bg-teal-50 text-teal-900",
  muted: "border-[var(--line)] bg-[var(--surface-2)] text-[var(--muted)]",
};

export default function GapPage() {
  const { meta, gap } = snapshot;
  const demandRows = gap.rows.filter((r) => r.status.startsWith("market_demand"));
  const lowRows = gap.rows.filter((r) => !r.status.startsWith("market_demand"));

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <header className="mb-6">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-[var(--accent)]">
          Portfolio Gap Analysis
        </p>
        <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Demanda de mercado vs. evidência real de portfólio
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-[var(--muted)]">
          Evidências vêm exclusivamente de{" "}
          <code className="font-mono text-xs">portfolio/evidence.yml</code> — registro manual e
          auditável. O sistema não atribui crédito por inferência nem elogia ninguém.
        </p>
      </header>

      {gap.rows.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--line)] bg-[var(--surface)] px-6 py-12 text-center">
          <p className="font-display text-lg font-semibold text-[var(--ink)]">
            Nenhuma skill atingiu o limiar de demanda ({gap.demand_threshold})
          </p>
          <p className="mt-2 text-sm text-[var(--muted)]">
            Amostra pequena demais para comparar com portfólio — estado honesto, sem número
            fabricado.
          </p>
        </div>
      ) : (
        <>
          <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
            <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
              Demanda ≥ {meta.demand_threshold} vagas ({demandRows.length})
            </h2>
            <ul className="mt-4 space-y-3">
              {demandRows.map((row) => {
                const status = gapStatus(row.status);
                return (
                  <li
                    key={row.skill}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-[var(--line)] bg-[var(--surface-2)] px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-[var(--ink)]">{row.skill}</p>
                      <p className="text-xs text-[var(--muted)]">
                        aparece em {row.market_frequency} vagas · evidência: {row.evidence_level}
                      </p>
                    </div>
                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${TONE_CLASSES[status.tone]}`}
                    >
                      {status.label}
                    </span>
                  </li>
                );
              })}
              {demandRows.length === 0 && (
                <li className="text-sm text-[var(--muted)]">Nenhuma skill atingiu o limiar.</li>
              )}
            </ul>
          </section>

          {lowRows.length > 0 && (
            <section className="mt-6 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
              <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
                Abaixo do limiar de demanda ({lowRows.length})
              </h2>
              <ul className="mt-4 grid gap-x-8 gap-y-2 text-sm sm:grid-cols-2 lg:grid-cols-3">
                {lowRows.map((row) => (
                  <li key={row.skill} className="flex justify-between">
                    <span className="text-[var(--ink)]">{row.skill}</span>
                    <span className="tabular-nums text-[var(--muted)]">{row.market_frequency}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}

      <footer className="mt-8 text-sm text-[var(--muted)]">
        Quer verificar uma evidência? Veja{" "}
        <Link href="/graph" className="text-[var(--accent)] underline-offset-2 hover:underline">
          o grafo do recorte completo
        </Link>{" "}
        ou o arquivo <code className="font-mono text-xs">portfolio/evidence.yml</code> no repositório.
      </footer>
    </main>
  );
}
