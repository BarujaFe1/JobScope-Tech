<div align="center">
  <img src="./icon.png" alt="JobScope Tech BR Logo" width="120" height="120" />

  <h1>JobScope Tech BR</h1>

  <p><strong>Produto de dados sobre o mercado de vagas tech no Brasil (spec V1 — docs).</strong></p>
  <p><strong>Data product for the Brazilian tech job market (V1 spec — docs).</strong></p>

  <p>
    <a href="#pt-br">PT-BR</a>
     · 
    <a href="#english">English</a>
     · 
    <a href="#stack">Stack</a>
     · 
    <a href="#architecture">Architecture</a>
     · 
    <a href="#quick-start">Quick Start</a>
     · 
    <a href="#author">Author</a>
  </p>

  <p>
    <img alt="Status-Spec%20%2F%20docs" src="https://img.shields.io/badge/Status-Spec%20%2F%20docs-0f766e?style=for-the-badge" />
    <img alt="Planned-Next.js" src="https://img.shields.io/badge/Planned-Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
    <img alt="Planned-FastAPI" src="https://img.shields.io/badge/Planned-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
    <img alt="License-MIT" src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
  </p>

  <p>
    <a href="https://github.com/BarujaFe1/JobScope-Tech"><strong>Repo</strong></a>
     · 
    <a href="https://barujafe.vercel.app/"><strong>Portfolio</strong></a>
     · 
    <a href="https://www.linkedin.com/in/barujafe/"><strong>LinkedIn</strong></a>
  </p>
</div>


> **Honest status:** this repository snapshot contains **README + LICENSE + icon only** (no application source). Content below reflects the **documented V1 product spec**, not shipped code in this clone.

---

## PT-BR

### Visão geral
O **JobScope Tech BR** é a especificação de um produto de dados para comparar e ler o mercado de vagas tech no Brasil: dashboard, lista, detalhe e pipeline — com stack alvo Next.js + FastAPI + PostgreSQL.

### Problema
Comparar vagas é difícil, dados são pouco estruturados e a leitura de mercado fica lenta/anedótica.

### Para quem
Candidatos e analistas que querem um **recorte estruturado** do mercado tech BR (quando o produto for implementado).

### Funcionalidades (V1 planejada / documentada)
- Dashboard de mercado
- Lista e detalhe de vagas
- Pipeline de dados (planejado)
- Escopo V1 enxuta com exclusões explícitas no README de produto

### Escopo e limites (honestos)
- **Docs-only** no Git atual — sem `package.json` / API no clone
- Não scraping ilegal; fontes e compliance devem ser definidos na implementação
- Sem demo pública no homepage

---

## English

### Overview
**JobScope Tech BR** is the spec for a data product to compare and read Brazil’s tech job market: dashboard, list, detail and pipeline — targeting Next.js + FastAPI + PostgreSQL.

### Problem
Job comparison is hard, data is poorly structured and market reading stays slow/anecdotal.

### Who it is for
Candidates and analysts who want a **structured slice** of the BR tech market (once implemented).

### Features (planned V1 / documented)
- Market dashboard
- Job list and detail
- Data pipeline (planned)
- Lean V1 scope with explicit non-goals in the product README

### Scope and honest limits
- **Docs-only** in current Git — no app source in this clone
- No illegal scraping; sources/compliance must be defined at implementation time
- No public homepage demo

---

## Stack

| Layer | Technology (planned) |
|---|---|
| Web | Next.js |
| API | FastAPI |
| DB | PostgreSQL |
| Repo today | README + LICENSE + icon |

---

## Architecture

Planned: ingest/normalize → store → dashboard/list/detail API → Next.js UI. See README history sections for V1 inclusions/exclusions.

---

## Quick Start

No runnable application is present in this repository snapshot. Use this README as the product brief until source is published.

---

## Technical decisions

- Keep **V1 lean** (documented non-goals matter)
- Prefer structured comparison over endless job-board scraping narratives
- Separate **spec repo honesty** from marketing screenshots of unshipped code

---

## Roadmap

- Publish initial app scaffold matching the V1 spec
- Define allowed data sources and refresh policy
- Add a lab demo with synthetic jobs first

---

## Author

**Felipe Alirio Baruja** — data / product / full-stack portfolio.

- Portfolio: [https://barujafe.vercel.app/](https://barujafe.vercel.app/)
- GitHub: [https://github.com/BarujaFe1](https://github.com/BarujaFe1)
- LinkedIn: [https://www.linkedin.com/in/barujafe/](https://www.linkedin.com/in/barujafe/)


## License

MIT — see [`LICENSE`](./LICENSE).
