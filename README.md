<div align="center">
  <img src="./assets/icon.png" alt="JobScope Tech BR" width="112" height="112" />

  <h1>JobScope Tech BR</h1>
  <p><strong>Vagas tech dispersas entram. Sinais de mercado saem.</strong></p>
  <p>Data product que transforma anúncios ruidosos do mercado brasileiro em um dashboard navegável.</p>

  <p>
    <img src="https://img.shields.io/badge/status-V1%20demo%20runnable-0f766e.svg" alt="V1 demo runnable" />
    <img src="https://img.shields.io/badge/backend-FastAPI-009688.svg?logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/frontend-Next.js-black.svg?logo=next.js&logoColor=white" alt="Next.js" />
    <img src="https://img.shields.io/badge/license-MIT-111827.svg" alt="MIT" />
  </p>

  <p>
    <a href="https://barujafe.vercel.app/"><strong>Portfólio</strong></a> ·
    <a href="https://github.com/BarujaFe1"><strong>GitHub</strong></a> ·
    <a href="https://www.linkedin.com/in/barujafe/"><strong>LinkedIn</strong></a>
  </p>
</div>

---

## Screenshot placeholder

> **TODO visual:** substituir por captura real do dashboard após o primeiro deploy.
>
> ![Dashboard placeholder](./assets/screenshot-dashboard-placeholder.svg)

---

## Problema real

Vagas tech no Brasil estão espalhadas em várias fontes, com títulos inconsistentes, skills misturadas a marketing e pouca padronização de senioridade/modalidade.

Perguntas simples — “o que o mercado pede agora?” — exigem ler dezenas (ou centenas) de anúncios manualmente.

## Solução

**JobScope Tech BR** é um pipeline + API + UI:

1. **Coleta** por fonte (V1: fixtures JSON com contrato de coletor)
2. **Parse** específico por fonte
3. **Normalização** de senioridade, modalidade e localidade
4. **Taxonomia** de skills por dicionário/aliases
5. **Deduplicação** pragmática por fingerprint
6. **Persistência** (SQLite demo / Postgres opcional)
7. **API FastAPI** + **dashboard Next.js**

## Principais funcionalidades (V1)

- Dashboard com totais, skills, senioridade, modalidade e localidades
- Lista de vagas com busca e filtros
- Detalhe da vaga (skills, fonte, fingerprint, descrição)
- Status do pipeline e histórico de runs
- Seed/demo data com 2 fontes e dedup cross-board
- Fallback demo no frontend se a API estiver offline

## Arquitetura

```txt
Fontes (fixtures) → Collectors/Parsers → Raw Jobs
  → Normalizers → Skill Taxonomy → Dedup → DB
  → FastAPI → Next.js
```

Detalhes: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Pydantic |
| Domínio | Normalizer, taxonomy, dedup (puro) |
| DB | SQLite (default) · PostgreSQL (Docker opcional) |
| Frontend | Next.js 15, TypeScript, Tailwind |
| Qualidade | pytest, Ruff, ESLint, GitHub Actions |

## Demo local

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- (Opcional) Docker para Postgres

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:3000  

### Variáveis de ambiente

Copie [`.env.example`](./.env.example) para `.env`. Principais:

| Variável | Função |
|---|---|
| `DATABASE_URL` | SQLite ou Postgres |
| `JOBSCOPE_DEMO_MODE` | Auto-seed no startup se DB vazio |
| `CORS_ORIGINS` | Origens do frontend |
| `NEXT_PUBLIC_API_URL` | Base da API no frontend |
| `NEXT_PUBLIC_DEMO_MODE` | Fallback de UI sem API |

## Testes

```bash
# Backend
cd backend && pytest -q && ruff check app tests scripts

# Frontend
cd frontend && npm run lint && npm run build
```

Guia: [`docs/TESTING.md`](./docs/TESTING.md)

## Decisões técnicas e trade-offs

- **Fixtures primeiro, scraping depois** — CI estável e sem risco de ToS na demo.
- **SQLite default** — clone → roda; Postgres quando precisar.
- **Taxonomia sem LLM** — explicável e testável.
- **Dedup simples** — evita duplicata óbvia; não resolve títulos divergentes.
- **Sem Alembic na V1** — `create_all` basta no schema atual.

Mais: [`docs/TECHNICAL_DECISIONS.md`](./docs/TECHNICAL_DECISIONS.md)

## Roadmap

- [x] Estrutura do monorepo + docs
- [x] Pipeline com 2 fontes fixture
- [x] API mínima + seed
- [x] Dashboard / lista / detalhe / pipeline
- [x] Testes + CI
- [ ] Screenshots e deploy público
- [ ] Coletor real (respeitando ToS)
- [ ] Postgres + migrations em produção
- [ ] Export CSV

## Status atual

**V1 demo runnable (2026-07).** O repositório deixou de ser “só README” e passou a instalar, testar e exibir um produto navegável com dados seed. Coleta ao vivo e deploy permanente ainda estão no roadmap.

Auditoria inicial: [`docs/AUDIT_REPORT.md`](./docs/AUDIT_REPORT.md) · Handoff: [`docs/HANDOFF.md`](./docs/HANDOFF.md)

## O que este projeto demonstra

- Pensamento de **data product** (não só scraper)
- Pipeline de dados bagunçados → sinal estruturado
- API clara e UI com estados vazios/demo
- Escopo disciplinado (o que **não** entra na V1)
- Documentação orientada a recrutador e entrevista
- Qualidade pública: testes, lint, CI

## Como eu apresentaria em entrevista

1. **Problema (30s):** mercado de vagas fragmentado e ruidoso no BR.
2. **Tese (30s):** coletar não basta — normalizar e classificar gera sinal.
3. **Arquitetura (1–2 min):** diagramar collectors → domain → DB → API → UI.
4. **Escolhas (1 min):** fixtures vs scrape; dicionário vs LLM; SQLite vs Postgres.
5. **Prova (1 min):** abrir dashboard, filtrar vagas, mostrar dedup NuvemPay e `/docs`.
6. **Próximo passo (20s):** um coletor real + deploy + screenshots.

## Docs

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)
- [`docs/TECHNICAL_DECISIONS.md`](./docs/TECHNICAL_DECISIONS.md)
- [`docs/TESTING.md`](./docs/TESTING.md)
- [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md)
- [`docs/AUDIT_REPORT.md`](./docs/AUDIT_REPORT.md)
- [`docs/HANDOFF.md`](./docs/HANDOFF.md)

## Autor

**Felipe Baruja** — [portfólio](https://barujafe.vercel.app/) · [GitHub](https://github.com/BarujaFe1) · [LinkedIn](https://www.linkedin.com/in/barujafe/)

## Licença

MIT — ver [`LICENSE`](./LICENSE).
