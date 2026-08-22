import { SiteHeader } from "@/components/SiteHeader";
import { DemoBanner, StatCard } from "@/components/ui";
import { getPipelineStatus } from "@/lib/api";
import { formatDate } from "@/lib/labels";

export default async function PipelinePage() {
  const { data, source } = await getPipelineStatus();

  return (
    <div className="min-h-screen">
      <SiteHeader active="pipeline" />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        <DemoBanner source={source} />

        <section className="mb-6 max-w-2xl">
          <h1 className="font-display text-3xl font-semibold tracking-tight">Pipeline</h1>
          <p className="mt-2 text-[var(--muted)]">
            Status das coletas por fonte. Na V1 as fontes são fixtures JSON — o mesmo contrato
            serve para coletores reais depois.
          </p>
        </section>

        <div className="mb-6 grid gap-4 sm:grid-cols-2">
          <StatCard
            label="Saúde"
            value={data.healthy ? "OK" : "Atenção"}
            hint={data.healthy ? "Sem falhas recentes" : "Há runs com status failed"}
          />
          <StatCard label="Fontes" value={data.sources.length} hint="Registradas no banco" />
        </div>

        <section className="mb-6 grid gap-4 md:grid-cols-2">
          {data.sources.map((sourceItem) => (
            <article
              key={sourceItem.key}
              className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]"
            >
              <h2 className="font-display text-lg font-semibold">{sourceItem.name}</h2>
              <p className="mt-1 font-mono text-xs text-[var(--muted)]">{sourceItem.key}</p>
              <p className="mt-3 text-sm text-[var(--muted)]">{sourceItem.description}</p>
            </article>
          ))}
        </section>

        <section className="overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--surface)] shadow-[var(--shadow-soft)]">
          <div className="border-b border-[var(--line)] px-5 py-4">
            <h2 className="font-display text-lg font-semibold">Runs recentes</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-[var(--surface-2)] text-[var(--muted)]">
                <tr>
                  <th className="px-4 py-3 font-medium">Fonte</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Coletadas</th>
                  <th className="px-4 py-3 font-medium">Criadas</th>
                  <th className="px-4 py-3 font-medium">Skipped</th>
                  <th className="px-4 py-3 font-medium">Quando</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_runs.map((run) => (
                  <tr key={run.id} className="border-t border-[var(--line)]">
                    <td className="px-4 py-3 font-mono text-xs">{run.source}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-md px-2 py-1 text-xs font-semibold ${
                          run.status === "success"
                            ? "bg-[var(--accent-soft)] text-[var(--accent)]"
                            : "bg-amber-100 text-amber-900"
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 tabular-nums">{run.jobs_collected}</td>
                    <td className="px-4 py-3 tabular-nums">{run.jobs_created}</td>
                    <td className="px-4 py-3 tabular-nums">{run.jobs_skipped}</td>
                    <td className="px-4 py-3 text-[var(--muted)]">{formatDate(run.started_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
