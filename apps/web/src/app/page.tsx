import Link from "next/link";

import { DistributionBars, StatCard } from "@/components/ui";
import { roleLabel, snapshot, type SliceGraph } from "@/lib/snapshot";

export default function OverviewPage() {
  const { meta, roles, skill_frequencies, graphs } = snapshot;
  const overall = skill_frequencies["_all"] ?? {};
  const topSkills = Object.entries(overall)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <header className="mb-8">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-[var(--accent)]">
          JobScope Signal Graph
        </p>
        <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight text-[var(--ink)]">
          O que as vagas de dados realmente pedem — medido, não adivinhado
        </h1>
        <p className="mt-3 max-w-2xl text-[var(--muted)]">
          Coleta pública (Greenhouse/Lever), skills extraídas por dicionário versionado{" "}
          <strong className="text-[var(--ink)]">com evidência textual</strong> e link da vaga
          original. Nenhum número aqui veio de feeling.
        </p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Vagas na amostra" value={meta.sample_size} hint={`modo: ${meta.mode ?? "snapshot"}`} />
        <StatCard label="Fontes" value={meta.sources.length} hint={meta.sources.map((s) => s.company).join(", ")} />
        <StatCard label="Skills mapeadas" value={Object.keys(overall).length} hint={`dicionário ${meta.skills_dictionary_version}`} />
        <StatCard
          label="Snapshot gerado em"
          value={new Date(meta.generated_at).toLocaleDateString("pt-BR")}
          hint={`metodologia v${meta.methodology_version}`}
        />
      </section>

      <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
        <strong>Amostra honesta:</strong> {meta.disclaimer}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <DistributionBars title="Vagas por role normalizada" data={Object.fromEntries(roles.map((r) => [roleLabel(r.role), r.jobs]))} />
        <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
          <h2 className="font-display text-lg font-semibold text-[var(--ink)]">Top skills na amostra</h2>
          <ol className="mt-4 space-y-2">
            {topSkills.map(([skill, count], i) => (
              <li key={skill} className="flex items-center gap-3 text-sm">
                <span className="w-5 tabular-nums text-[var(--muted)]">{i + 1}.</span>
                <span className="flex-1 text-[var(--ink)]">{skill}</span>
                <span className="tabular-nums text-[var(--muted)]">{count}</span>
              </li>
            ))}
            {topSkills.length === 0 && (
              <li className="text-sm text-[var(--muted)]">Sem skills detectadas nesta amostra.</li>
            )}
          </ol>
        </section>
      </div>

      <nav className="mt-8 grid gap-4 sm:grid-cols-3">
        <Link
          href="/graph"
          className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)] transition hover:border-[var(--accent)]"
        >
          <p className="font-display text-lg font-semibold text-[var(--ink)]">Grafo de coocorrência →</p>
          <p className="mt-2 text-sm text-[var(--muted)]">
            Quais skills aparecem juntas ({graphs._all?.edges.length ?? 0} arestas ≥ suporte {meta.min_support}).
          </p>
        </Link>
        <Link
          href="/gap"
          className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)] transition hover:border-[var(--accent)]"
        >
          <p className="font-display text-lg font-semibold text-[var(--ink)]">Portfolio Gap →</p>
          <p className="mt-2 text-sm text-[var(--muted)]">
            Demanda de mercado vs evidências registradas do portfólio.
          </p>
        </Link>
        <Link
          href="/roles/data_analyst"
          className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)] transition hover:border-[var(--accent)]"
        >
          <p className="font-display text-lg font-semibold text-[var(--ink)]">Bundles por role →</p>
          <p className="mt-2 text-sm text-[var(--muted)]">
            Combinações mais frequentes por cargo.
          </p>
        </Link>
      </nav>

      <SlicePeek graphs={graphs} />
    </main>
  );
}

function SlicePeek({ graphs }: { graphs: Record<string, SliceGraph> }) {
  const all = graphs["_all"];
  if (!all || all.edges.length === 0) {
    return null;
  }
  const top = all.edges.slice(0, 5);
  return (
    <section className="mt-8 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
      <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
        Combinações mais fortes (amostra inteira)
      </h2>
      <ul className="mt-4 space-y-2 text-sm">
        {top.map((e) => (
          <li key={`${e.skill_a}|${e.skill_b}`} className="flex items-center justify-between">
            <span className="text-[var(--ink)]">
              {e.skill_a} <span className="text-[var(--muted)]">×</span> {e.skill_b}
            </span>
            <span className="tabular-nums text-[var(--muted)]">
              suporte {e.support} · jaccard {e.jaccard.toFixed(2)}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
