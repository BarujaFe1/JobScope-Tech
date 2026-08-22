import Link from "next/link";

const links = [
  { href: "/", label: "Visão geral" },
  { href: "/graph", label: "Grafo" },
  { href: "/gap", label: "Portfolio Gap" },
];

export function SiteHeader() {
  return (
    <header className="border-b border-[var(--line)] bg-[var(--surface)]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link href="/" className="group flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/icon.png"
            alt=""
            width={40}
            height={40}
            className="h-10 w-10 rounded-lg object-cover shadow-sm ring-1 ring-[var(--line)] transition group-hover:scale-[1.03]"
          />
          <div>
            <p className="font-display text-lg font-semibold tracking-tight text-[var(--ink)]">
              JobScope Signal Graph
            </p>
            <p className="text-xs text-[var(--muted)]">Medindo vagas de dados, não adivinhando</p>
          </div>
        </Link>
        <nav aria-label="Principal" className="flex items-center gap-1 sm:gap-2">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                link.href === "/"
                  ? "text-[var(--muted)] hover:bg-[var(--surface-2)] hover:text-[var(--ink)]"
                  : "text-[var(--muted)] hover:bg-[var(--surface-2)] hover:text-[var(--ink)]"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
