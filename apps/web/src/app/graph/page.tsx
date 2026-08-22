import Link from "next/link";

import { EmptyState } from "@/components/ui";
import { roleLabel, snapshot } from "@/lib/snapshot";

export default async function GraphPage({
  searchParams,
}: {
  searchParams: Promise<{ slice?: string }>;
}) {
  const params = await searchParams;
  const sliceKey = params.slice ?? "_all";
  const { meta, graphs } = snapshot;
  const graph = graphs[sliceKey];

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <header className="mb-6">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-[var(--accent)]">
          Grafo de coocorrência
        </p>
        <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Skills que aparecem juntas
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-[var(--muted)]">
          Uma aresta existe só se o par coocorrer em ≥{" "}
          {graph?.min_support ?? meta.min_support} vagas do recorte — abaixo disso,{" "}
          <strong className="text-[var(--ink)]">o par simplesmente não aparece</strong>. Métrica:
          suporte absoluto + Jaccard.
        </p>
      </header>

      <nav className="mb-6 flex flex-wrap gap-2">
        {Object.keys(graphs).map((key) => (
          <Link
            key={key}
            href={`/graph?slice=${encodeURIComponent(key)}`}
            className={`rounded-full border px-3 py-1.5 text-sm transition ${
              key === sliceKey
                ? "border-[var(--accent)] bg-[var(--accent)] text-white"
                : "border-[var(--line)] text-[var(--muted)] hover:border-[var(--accent)]"
            }`}
          >
            {key === "_all" ? "Amostra inteira" : roleLabel(key)}
          </Link>
        ))}
      </nav>

      {!graph ? (
        <EmptyState
          title="Recorte não encontrado"
          body={`Não há dados para "${sliceKey}" neste snapshot. Escolha um dos recortes acima.`}
        />
      ) : graph.edges.length === 0 ? (
        <EmptyState
          title="Nenhuma aresta acima do suporte mínimo"
          body={`Com ${graph.nodes.length} skills e o suporte mínimo ${graph.min_support}, nenhum par coocorreu o suficiente neste recorte. Honestidade > gráfico bonito.`}
        />
      ) : (
        <>
          <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
            <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
              Arestas ({graph.edges.length})
            </h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--line)] text-left text-xs uppercase tracking-wide text-[var(--muted)]">
                    <th className="pb-2 pr-4">Par</th>
                    <th className="pb-2 pr-4">Suporte</th>
                    <th className="pb-2">Jaccard</th>
                  </tr>
                </thead>
                <tbody>
                  {graph.edges.map((e) => (
                    <tr key={`${e.skill_a}|${e.skill_b}`} className="border-b border-[var(--line)]/50">
                      <td className="py-2 pr-4 text-[var(--ink)]">
                        {e.skill_a} × {e.skill_b}
                      </td>
                      <td className="py-2 pr-4 tabular-nums">{e.support}</td>
                      <td className="py-2 tabular-nums">{e.jaccard.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="mt-6 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
            <h2 className="font-display text-lg font-semibold text-[var(--ink)]">Bundles</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">
              Vizinhos mais fortes de cada skill (top {graph.edges.length} por suporte).
            </p>
            <ul className="mt-4 space-y-3">
              {Object.entries(graph.bundles).map(([skill, neighbors]) => (
                <li key={skill} className="text-sm">
                  <span className="font-medium text-[var(--ink)]">{skill}</span>
                  <span className="text-[var(--muted)]"> → {neighbors.join(", ")}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="mt-6 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
            <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
              Frequências do recorte ({graph.nodes.length} skills)
            </h2>
            <ul className="mt-4 grid gap-x-8 gap-y-2 text-sm sm:grid-cols-2 lg:grid-cols-3">
              {graph.nodes.map((n) => (
                <li key={n.skill} className="flex justify-between">
                  <span className="text-[var(--ink)]">{n.skill}</span>
                  <span className="tabular-nums text-[var(--muted)]">{n.frequency}</span>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </main>
  );
}
