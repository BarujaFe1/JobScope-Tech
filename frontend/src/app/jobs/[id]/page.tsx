import Link from "next/link";
import { notFound } from "next/navigation";
import { SiteHeader } from "@/components/SiteHeader";
import { DemoBanner } from "@/components/ui";
import { getJob } from "@/lib/api";
import { formatDate, labelSeniority, labelWorkModel } from "@/lib/labels";

type Params = Promise<{ id: string }>;

export default async function JobDetailPage({ params }: { params: Params }) {
  const { id } = await params;
  const jobId = Number(id);
  if (!Number.isFinite(jobId)) {
    notFound();
  }

  const { data: job, source } = await getJob(jobId);
  if (!job) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <SiteHeader active="jobs" />
      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-10">
        <DemoBanner source={source} />
        <Link href="/jobs" className="text-sm font-medium text-[var(--accent)] hover:underline">
          ← Voltar para vagas
        </Link>

        <article className="mt-4 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-6 shadow-[var(--shadow-soft)]">
          <p className="text-sm text-[var(--muted)]">{job.company}</p>
          <h1 className="mt-1 font-display text-3xl font-semibold tracking-tight text-[var(--ink)]">
            {job.title}
          </h1>
          <p className="mt-2 text-[var(--muted)]">
            {job.location} · {labelSeniority(job.seniority)} · {labelWorkModel(job.work_model)}
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            {job.skills.map((skill) => (
              <span
                key={skill}
                className="rounded-md bg-[var(--accent-soft)] px-2.5 py-1 text-xs font-medium text-[var(--accent)]"
              >
                {skill}
              </span>
            ))}
          </div>

          <dl className="mt-6 grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-[var(--muted)]">Fonte</dt>
              <dd className="font-medium">{job.source}</dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">Publicada</dt>
              <dd className="font-medium">{formatDate(job.published_at)}</dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">Coletada</dt>
              <dd className="font-medium">{formatDate(job.collected_at)}</dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">Fingerprint</dt>
              <dd className="font-mono text-xs">{job.fingerprint}</dd>
            </div>
          </dl>

          <div className="mt-6 border-t border-[var(--line)] pt-6">
            <h2 className="font-display text-lg font-semibold">Descrição</h2>
            <p className="mt-3 whitespace-pre-wrap text-[var(--ink)]/90 leading-relaxed">
              {job.description}
            </p>
          </div>

          <a
            href={job.original_url}
            target="_blank"
            rel="noreferrer"
            className="mt-6 inline-flex rounded-md border border-[var(--line)] px-4 py-2 text-sm font-semibold text-[var(--ink)] transition hover:bg-[var(--surface-2)]"
          >
            Abrir link original
          </a>
        </article>
      </main>
    </div>
  );
}
