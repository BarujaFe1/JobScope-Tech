import Link from "next/link";
import { notFound } from "next/navigation";

import { EmptyState } from "@/components/ui";
import { roleLabel, snapshot } from "@/lib/snapshot";

export function generateStaticParams() {
  return Object.keys(snapshot.graphs)
    .filter((key) => key !== "_all")
    .map((role) => ({ role }));
}

export default async function RolePage({ params }: { params: Promise<{ role: string }> }) {
  const { role } = await params;
  const graph = snapshot.graphs[role];
  const summary = snapshot.roles.find((r) => r.role === role);
  const freqs = snapshot.skill_frequencies[role] ?? {};

  if (!graph && !summary) {
    notFound();
  }

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <header className="mb-6">
        <Link href="/" className="text-sm text-[var(--accent)] underline-offset-2 hover:underline">
          ← visão geral
        </Link>
        <h1 className="mt-3 font-display text-3xl font-semibold tracking-tight text-[var(--ink)]">
          {roleLabel(role)}
        </h1>
        <p className="mt-2 text-sm text-[var(--muted)]">
          {summary ? `${summary.jobs} vagas nesta amostra` : "Sem vagas neste recorte"} · suporte
          mínimo {graph?.min_support ?? snapshot.meta.min_support} arestas
        </p>
      </header>

      {!graph || graph.nodes.length === 0 ? (
        <EmptyState
          title="Sem skills suficientes neste recorte"
          body="Com poucas vagas classificadas nesta role, exibir bundles seria inventar padrão. Volte quando a amostra crescer."
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
            <h2 className="font-display text-lg font-semibold text-[var(--ink)]">Skills mais pedidas</h2>
            <ul className="mt-4 space-y-2 text-sm">
              {Object.entries(freqs)
                .sort((a, b) => b[1] - a[1])
                .map(([skill, count]) => (
                  <li key={skill} className="flex justify-between">
                    <span className="text-[var(--ink)]">{skill}</span>
                    <span className="tabular-nums text-[var(--muted)]">{count}</span>
                  </li>
                ))}
            </ul>
          </section>

          <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-soft)]">
            <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
              Bundles (aparecem juntos)
            </h2>
            <ul className="mt-4 space-y-3 text-sm">
              {Object.entries(graph.bundles).map(([skill, neighbors]) => (
                <li key={skill}>
                  <span className="font-medium text-[var(--ink)]">{skill}</span>
                  <span className="text-[var(--muted)]"> → {neighbors.join(", ")}</span>
                </li>
              ))}
              {Object.keys(graph.bundles).length === 0 && (
                <li className="text-[var(--muted)]">
                  Nenhum par atingiu o suporte mínimo nesta role.
                </li>
              )}
            </ul>
            <Link
              href={`/graph?slice=${encodeURIComponent(role)}`}
              className="mt-4 inline-block text-sm text-[var(--accent)] underline-offset-2 hover:underline"
            >
              ver grafo completo deste recorte →
            </Link>
          </section>
        </div>
      )}
    </main>
  );
}
