import rawSnapshot from "@/data/market_snapshot.json";

export interface SnapshotMeta {
  generated_at: string;
  methodology_version: string;
  skills_dictionary_version: string;
  sample_size: number;
  mode?: string;
  sources: Array<{
    company: string;
    ats: string;
    identifier?: string;
    country?: string;
    scope?: string;
    jobs_captured: number;
  }>;
  demand_threshold?: number;
  min_support?: number;
  dedup?: { total_input: number; same_key_collapsed: number; cross_source_hash_collapsed: number };
  disclaimer: string;
}

export interface RoleSummary {
  role: string;
  jobs: number;
}

export interface GraphNode {
  skill: string;
  frequency: number;
}

export interface GraphEdge {
  skill_a: string;
  skill_b: string;
  support: number;
  jaccard: number;
}

export interface SliceGraph {
  min_support: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
  bundles: Record<string, string[]>;
}

export interface GapRow {
  skill: string;
  market_frequency: number;
  evidence_level: string;
  status: string;
}

export interface EvidenceExample {
  skill: string;
  snippet: string;
  source_url: string;
  company: string;
}

export interface MarketSnapshot {
  meta: SnapshotMeta;
  roles: RoleSummary[];
  skill_frequencies: Record<string, Record<string, number>>;
  graphs: Record<string, SliceGraph>;
  evidence_examples: EvidenceExample[];
  gap: { demand_threshold: number; rows: GapRow[] };
}

export const snapshot = rawSnapshot as unknown as MarketSnapshot;

export const ROLE_LABELS: Record<string, string> = {
  analytics_engineer: "Analytics Engineer",
  data_analyst: "Data Analyst",
  product_analyst: "Product Analyst",
  data_scientist: "Data Scientist",
  data_engineer: "Data Engineer",
  other: "Other / não classificado",
};

export function roleLabel(role: string): string {
  return ROLE_LABELS[role] ?? role;
}

const STATUS_LABELS: Record<string, { label: string; tone: "demand" | "ok" | "muted" }> = {
  market_demand_no_evidence: { label: "demanda alta · sem evidência", tone: "demand" },
  market_demand_with_evidence: { label: "demanda alta · com evidência", tone: "ok" },
  low_demand_with_evidence: { label: "demanda baixa · com evidência", tone: "muted" },
  low_demand_no_evidence: { label: "demanda baixa · sem evidência", tone: "muted" },
};

export function gapStatus(status: string): { label: string; tone: "demand" | "ok" | "muted" } {
  return STATUS_LABELS[status] ?? { label: status, tone: "muted" };
}
