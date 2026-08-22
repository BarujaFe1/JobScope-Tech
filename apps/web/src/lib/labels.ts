export function labelSeniority(value: string): string {
  const map: Record<string, string> = {
    intern: "Estágio",
    junior: "Júnior",
    mid: "Pleno",
    senior: "Sênior",
    lead: "Lead",
    unspecified: "Não informado",
  };
  return map[value] ?? value;
}

export function labelWorkModel(value: string): string {
  const map: Record<string, string> = {
    remote: "Remoto",
    hybrid: "Híbrido",
    onsite: "Presencial",
    unspecified: "Não informado",
  };
  return map[value] ?? value;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}
