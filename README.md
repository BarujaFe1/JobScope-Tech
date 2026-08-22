<div align="center">
  <img src="./assets/icon.png" alt="JobScope Signal Graph" width="112" height="112" />

  <h1>JobScope Signal Graph</h1>
  <p><strong>Eu estava escolhendo projetos para entrar em Dados. Parei de adivinhar e comecei a medir as vagas.</strong></p>
  <p>Produto de dados que mede quais skills aparecem <em>juntas</em> em vagas reais de Dados/Analytics (boards públicos Greenhouse/Lever) e compara demanda de mercado com evidências verificáveis de portfólio.</p>
</div>

---

## O problema

Escolher o que estudar (ou contratar) em Dados é chute: títulos inconsistentes, skills misturadas a marketing, senioridades sem padrão. Um "dashboard de vagas" comum conta frequências isoladas — mas **o que define um stack real é o que aparece junto**.

## Por que não é trivial

- **Coexistência ≠ correlação óbvia**: precisa de grafo de coocorrência com gate de suporte mínimo para não desenhar arestas por ruído;
- **Evidência ou não aconteceu**: cada skill detectada carrega o *span* do texto original + link da vaga — nada de número sem prova;
- **Dedup entre ATS**: mesma vaga publicada em boards diferentes colapsa por hash canônico do texto;
- **Gap honesto**: o comparativo portfólio-vs-mercado só usa evidências manualmente registradas (`portfolio/evidence.yml`) — o sistema não elogia nem inventa.

## Arquitetura

```txt
data/config/sources.yml ──→ apps/api (FastAPI · httpx · Pydantic)
                              ├ adapters/greenhouse.py  GET /v1/boards/{token}/jobs?content=true
                              ├ adapters/lever.py       GET /v0/postings/{site}?mode=json
                              ├ services/ snapshot → skills → roles → graph → gap
scripts/build_snapshot.py ──→ data/public/market_snapshot.json (agregados + snippets ≤200 chars)
apps/web (Next.js 15)     ──→ lê o snapshot commitado: overview · grafo · bundles · gap
```

Detalhes: [`docs/METHODOLOGY.md`](./docs/METHODOLOGY.md) · [`docs/SOURCES_AND_COMPLIANCE.md`](./docs/SOURCES_AND_COMPLIANCE.md)

## Quickstart

```bash
# API + testes (Python 3.12+)
cd apps/api
python -m venv .venv && .venv\Scripts\activate   # Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                                        # 69 testes, incluindo os 7 golden scenarios

# Snapshot sintético (determinístico) ou real (boards habilitados):
python ../../scripts/build_snapshot.py --mode synthetic
python ../../scripts/build_snapshot.py --mode live

# Web
cd ../web
npm ci && npm run sync:snapshot && npm run dev   # http://localhost:3000
```

## Momento principal (≤3 cliques)

1. abrir **Visão geral** → amostra, fontes e top skills com disclaimers;
2. clicar **Grafo** → pares SQL×Python etc. com suporte/Jaccard (arestas fracas *não existem*);
3. clicar **Portfolio Gap** → demanda vs evidências auditáveis, status factual por skill.

## Limitações honestas

- amostra = apenas boards Greenhouse/Lever habilitados (**Gupy está fora de escopo**) — não é retrato do mercado BR completo;
- extração por dicionário versionado: recall limitado, zero magia, zero LLM nesta versão;
- snapshot é corte temporal; séries históricas exigem capturas recorrentes.

## Qualidade (factual, sem overclaim)

| Check | Estado |
|---|---|
| Testes automatizados | 69 passing (unit + integração + 7 golden scenarios G1–G7) |
| Lint Python | ruff clean |
| Web lint + build | ESLint clean, Next build OK |
| CI | GitHub Actions: ruff+pytest / eslint+build |
| Secret/PII scan | script dedicado no CI |

## Screenshots

> Capturas do build publicado: ver `assets/screenshots/` (atualizadas pós-deploy).

## Autor

**Felipe Baruja** — [portfólio](https://barujafe.vercel.app/) · [GitHub](https://github.com/BarujaFe1) · [LinkedIn](https://www.linkedin.com/in/barujafe/)

## Licença

MIT — ver [`LICENSE`](./LICENSE).
