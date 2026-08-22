export type Skill = {
  id: number;
  name: string;
  category: string;
  slug: string;
  count?: number | null;
};

export type JobListItem = {
  id: number;
  title: string;
  company: string;
  seniority: string;
  work_model: string;
  location: string;
  source: string;
  original_url: string;
  skills: string[];
  published_at: string | null;
  collected_at: string;
};

export type JobDetail = JobListItem & {
  description: string;
  fingerprint: string;
  external_id: string;
};

export type JobsPage = {
  items: JobListItem[];
  total: number;
  page: number;
  page_size: number;
};

export type Stats = {
  total_jobs: number;
  unique_companies: number;
  top_skills: Skill[];
  seniority_distribution: Record<string, number>;
  work_model_distribution: Record<string, number>;
  top_locations: Record<string, number>;
};

export type PipelineStatus = {
  sources: { key: string; name: string; description: string | null }[];
  recent_runs: {
    id: number;
    source: string;
    status: string;
    started_at: string;
    finished_at: string | null;
    jobs_collected: number;
    jobs_created: number;
    jobs_skipped: number;
    message: string | null;
  }[];
  healthy: boolean;
};

export type JobFilters = {
  page?: number;
  page_size?: number;
  seniority?: string;
  work_model?: string;
  skill?: string;
  q?: string;
};
