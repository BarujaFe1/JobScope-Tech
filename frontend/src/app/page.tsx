import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { DemoBanner, DistributionBars, StatCard } from "@/components/ui";
import { getStats } from "@/lib/api";
import { labelSeniority, labelWorkModel } from "@/lib/labels";

export default async function HomePage() {
  const { data: stats, source } = await getStats();
  const topSkill = stats.top_skills[0];

  return (
    <div className="min-h-screen">
      <SiteHeader active="dashboard" />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        <DemoBanner source={source} />

        <section className="animate-rise mb-8 max-w-2xl">
          <p className="text-sm font-medium uppercase tracking-[0.16em] text-[var(--accent)]">
            Mercado tech BR
          </p>
          <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight text-[var(--ink)] sm:text-4xl">
            O que o mercado está pedindo — com dados limpos
          </h1>
          <p className="mt-3 text-base text-[var(--muted)] sm:text-lg">
            JobScope coleta, normaliza e classifica vagas tech para revelar skills, senioridade e
            modalidades sem você ler centenas de anúncios.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              href="/jobs"
              className="rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-white transition hover:brightness-110"
            >
              Explorar vagas
            </Link>
            <Link
              href="/pipeline"
              className="rounded-md border border-[var(--line)] bg-[var(--surface)] px-4 py-2.5 text-sm font-semibold text-[var(--ink)] transition hover:bg-[var(--surface-2)]"
            >
              Ver pipeline
            </Link>
          </div>
        </section>

        <section className="animate-rise-delay-1 mb-6 grid gap-4 sm:grid-cols-3">
          <StatCard label="Vagas" value={stats.total_jobs} hint="Após deduplicação" />
          <StatCard
            label="Empresas"
            value={stats.unique_companies}
            hint="Nomes normalizados"
          />
          <StatCard
            label="Skill #1"
            value={topSkill?.name ?? "—"}
            hint={topSkill ? `${topSkill.count} menções` : "Sem dados"}
          />
        </section>

        <section className="animate-rise-delay-2 grid gap-4 lg:grid-cols-2">
          <DistributionBars
            title="Senioridade"
            data={stats.seniority_distribution}
            labelFn={labelSeniority}
          />
          <DistributionBars
            title="Modalidade"
            data={stats.work_model_distribution}
            labelFn={labelWorkModel}
          />
          <DistributionBars title="Localidades" data={stats.top_locations} />
          <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
            <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
              Skills mais pedidas
            </h2>
            <ul className="mt-4 space-y-3">
              {stats.top_skills.slice(0, 8).map((skill) => {
                const max = stats.top_skills[0]?.count ?? 1;
                const count = skill.count ?? 0;
                return (
                  <li key={skill.id}>
                    <div className="mb-1 flex items-center justify-between text-sm">
                      <span>
                        <span className="font-medium text-[var(--ink)]">{skill.name}</span>
                        <span className="ml-2 text-xs text-[var(--muted)]">{skill.category}</span>
                      </span>
                      <span className="tabular-nums text-[var(--muted)]">{count}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-[var(--surface-2)]">
                      <div
                        className="h-full rounded-full bg-[var(--ink)]/80 transition-all duration-700"
                        style={{ width: `${(count / max) * 100}%` }}
                      />
                    </div>
                  </li>
                );
              })}
            </ul>
          </section>
        </section>
      </main>
    </div>
  );
}
