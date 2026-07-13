import type { JobDetail, JobFilters, JobsPage, PipelineStatus, Skill, Stats } from "./types";
import { DEMO_JOBS, DEMO_PIPELINE, DEMO_SKILLS, DEMO_STATS } from "./demo-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DEMO_MODE = (process.env.NEXT_PUBLIC_DEMO_MODE ?? "true").toLowerCase() !== "false";

export type ApiSource = "api" | "demo";

async function fetchJson<T>(path: string): Promise<{ data: T; source: ApiSource }> {
  try {
    const res = await fetch(`${API_URL}${path}`, {
      next: { revalidate: 30 },
    });
    if (!res.ok) {
      throw new Error(`API ${res.status}`);
    }
    return { data: (await res.json()) as T, source: "api" };
  } catch {
    if (!DEMO_MODE) {
      throw new Error(`Falha ao contatar a API em ${API_URL}${path}`);
    }
    throw new Error("DEMO_FALLBACK");
  }
}

export async function getStats(): Promise<{ data: Stats; source: ApiSource }> {
  try {
    return await fetchJson<Stats>("/stats");
  } catch {
    return { data: DEMO_STATS, source: "demo" };
  }
}

export async function getSkills(): Promise<{ data: Skill[]; source: ApiSource }> {
  try {
    return await fetchJson<Skill[]>("/skills");
  } catch {
    return { data: DEMO_SKILLS, source: "demo" };
  }
}

export async function getJobs(
  filters: JobFilters = {},
): Promise<{ data: JobsPage; source: ApiSource }> {
  const params = new URLSearchParams();
  if (filters.page) params.set("page", String(filters.page));
  if (filters.page_size) params.set("page_size", String(filters.page_size));
  if (filters.seniority) params.set("seniority", filters.seniority);
  if (filters.work_model) params.set("work_model", filters.work_model);
  if (filters.skill) params.set("skill", filters.skill);
  if (filters.q) params.set("q", filters.q);
  const qs = params.toString();
  try {
    return await fetchJson<JobsPage>(`/jobs${qs ? `?${qs}` : ""}`);
  } catch {
    let items = [...DEMO_JOBS];
    if (filters.seniority) {
      items = items.filter((j) => j.seniority === filters.seniority);
    }
    if (filters.work_model) {
      items = items.filter((j) => j.work_model === filters.work_model);
    }
    if (filters.skill) {
      const needle = filters.skill.toLowerCase();
      items = items.filter((j) =>
        j.skills.some((s) => s.toLowerCase() === needle || s.toLowerCase().includes(needle)),
      );
    }
    if (filters.q) {
      const q = filters.q.toLowerCase();
      items = items.filter(
        (j) => j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q),
      );
    }
    const page = filters.page ?? 1;
    const pageSize = filters.page_size ?? 20;
    const start = (page - 1) * pageSize;
    return {
      data: {
        items: items.slice(start, start + pageSize),
        total: items.length,
        page,
        page_size: pageSize,
      },
      source: "demo",
    };
  }
}

export async function getJob(id: number): Promise<{ data: JobDetail | null; source: ApiSource }> {
  try {
    return await fetchJson<JobDetail>(`/jobs/${id}`);
  } catch {
    const job = DEMO_JOBS.find((j) => j.id === id) ?? null;
    return { data: job, source: "demo" };
  }
}

export async function getPipelineStatus(): Promise<{ data: PipelineStatus; source: ApiSource }> {
  try {
    return await fetchJson<PipelineStatus>("/pipeline/status");
  } catch {
    return { data: DEMO_PIPELINE, source: "demo" };
  }
}
