import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { DemoBanner, EmptyState } from "@/components/ui";
import { getJobs } from "@/lib/api";
import { formatDate, labelSeniority, labelWorkModel } from "@/lib/labels";

type SearchParams = Promise<{
  seniority?: string;
  work_model?: string;
  q?: string;
  page?: string;
}>;

export default async function JobsPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const page = Number(params.page ?? "1") || 1;
  const { data, source } = await getJobs({
    page,
    page_size: 12,
    seniority: params.seniority,
    work_model: params.work_model,
    q: params.q,
  });

  return (
    <div className="min-h-screen">
      <SiteHeader active="jobs" />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        <DemoBanner source={source} />

        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="font-display text-3xl font-semibold tracking-tight">Vagas</h1>
            <p className="mt-1 text-[var(--muted)]">
              {data.total} resultado{data.total === 1 ? "" : "s"} após filtros
            </p>
          </div>
        </div>

        <form className="mb-6 grid gap-3 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-4 shadow-[var(--shadow-soft)] sm:grid-cols-4">
          <label className="block text-sm">
            <span className="mb-1 block text-[var(--muted)]">Busca</span>
            <input
              name="q"
              defaultValue={params.q ?? ""}
              placeholder="Título ou empresa"
              className="w-full rounded-md border border-[var(--line)] bg-white px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-[var(--muted)]">Senioridade</span>
            <select
              name="seniority"
              defaultValue={params.seniority ?? ""}
              className="w-full rounded-md border border-[var(--line)] bg-white px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
            >
              <option value="">Todas</option>
              {["intern", "junior", "mid", "senior", "lead"].map((v) => (
                <option key={v} value={v}>
                  {labelSeniority(v)}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-[var(--muted)]">Modalidade</span>
            <select
              name="work_model"
              defaultValue={params.work_model ?? ""}
              className="w-full rounded-md border border-[var(--line)] bg-white px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
            >
              <option value="">Todas</option>
              {["remote", "hybrid", "onsite"].map((v) => (
                <option key={v} value={v}>
                  {labelWorkModel(v)}
                </option>
              ))}
            </select>
          </label>
          <div className="flex items-end">
            <button
              type="submit"
              className="w-full rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-white transition hover:brightness-110"
            >
              Filtrar
            </button>
          </div>
        </form>

        {data.items.length === 0 ? (
          <EmptyState
            title="Nenhuma vaga encontrada"
            body="Ajuste os filtros ou rode o seed do backend para popular a base demo."
          />
        ) : (
          <ul className="space-y-3">
            {data.items.map((job) => (
              <li key={job.id}>
                <Link
                  href={`/jobs/${job.id}`}
                  className="block rounded-xl border border-[var(--line)] bg-[var(--surface)] p-4 shadow-[var(--shadow-soft)] transition hover:-translate-y-0.5 hover:border-[var(--accent)]/40"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
                        {job.title}
                      </h2>
                      <p className="text-sm text-[var(--muted)]">
                        {job.company} · {job.location}
                      </p>
                    </div>
                    <p className="text-xs text-[var(--muted)]">{formatDate(job.published_at)}</p>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="rounded-md bg-[var(--accent-soft)] px-2 py-1 text-xs font-medium text-[var(--accent)]">
                      {labelSeniority(job.seniority)}
                    </span>
                    <span className="rounded-md bg-[var(--surface-2)] px-2 py-1 text-xs font-medium text-[var(--ink)]">
                      {labelWorkModel(job.work_model)}
                    </span>
                    {job.skills.slice(0, 5).map((skill) => (
                      <span
                        key={skill}
                        className="rounded-md border border-[var(--line)] px-2 py-1 text-xs text-[var(--muted)]"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}

        {data.total > data.page_size ? (
          <div className="mt-6 flex items-center justify-between text-sm">
            <p className="text-[var(--muted)]">
              Página {data.page} · {data.total} total
            </p>
            <div className="flex gap-2">
              {data.page > 1 ? (
                <Link
                  className="rounded-md border border-[var(--line)] bg-white px-3 py-1.5"
                  href={`/jobs?page=${data.page - 1}${params.seniority ? `&seniority=${params.seniority}` : ""}${params.work_model ? `&work_model=${params.work_model}` : ""}${params.q ? `&q=${encodeURIComponent(params.q)}` : ""}`}
                >
                  Anterior
                </Link>
              ) : null}
              {data.page * data.page_size < data.total ? (
                <Link
                  className="rounded-md border border-[var(--line)] bg-white px-3 py-1.5"
                  href={`/jobs?page=${data.page + 1}${params.seniority ? `&seniority=${params.seniority}` : ""}${params.work_model ? `&work_model=${params.work_model}` : ""}${params.q ? `&q=${encodeURIComponent(params.q)}` : ""}`}
                >
                  Próxima
                </Link>
              ) : null}
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
}
