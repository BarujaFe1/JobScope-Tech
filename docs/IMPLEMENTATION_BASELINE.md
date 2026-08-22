# Implementation Baseline — JobScope Signal Graph

**Date:** 2026-08-22
**Auditor:** agentic IDE (opencode)
**Context pack:** `PROJECT_CONTEXT_PACK.zip` (2026-08-22) + `SUPERMEGAPROMPT.md`

## Preflight verificado

```text
BASELINE_HEAD          = bf967f0443442bacac903378a9bb048004baf27c  (confere com o pack — sem drift)
BASELINE_BRANCH        = main (default, desprotegida)
WORKING_TREE           = clean
REMOTE                 = https://github.com/BarujaFe1/JobScope-Tech.git
UNMERGED_WORK_FOUND    = SIM — origin/chore/portfolio-quality-pass @ f7aab7b3f69f
CURRENT_DEPLOY         = NENHUM (repo sem config de deploy, sem GitHub Pages)
BASELINE_TESTS         = main: 0 · strandada: pytest suite recuperável (3 arquivos)
```

## Arquitetura atual (main @ bf967f0)

Docs-only: `README.md` (template bilíngue de portfólio) + `LICENSE` (MIT) + `icon.png`.
Nenhum código executável. O próprio README declara esse estado.

## Trabalho strandado recuperado (`chore/portfolio-quality-pass` @ f7aab7b)

1 commit à frente do merge-base `3a8e130`, **divergido de main por 1 commit**
(main avançou com rewrite do README; a branch reescreveu o README em outra direção).
68 arquivos: V1 fixture-based completa.

- **backend/** FastAPI + SQLAlchemy 2.0 + Pydantic v2: domain (normalizer senioridade/
  modalidade PT-BR, taxonomy dict+aliases sem LLM, dedup SHA-256 título|empresa),
  pipeline fixtures→persist, rotas `/health /jobs /jobs/{id} /stats /skills /pipeline/*`,
  SQLite default, seed CLI, **testes**: `test_api.py` (integração c/ TestClient,
  inclui dedup cross-board) + `test_domain.py` (unit).
- **frontend/** Next.js 15.1 + React 19 + Tailwind 3: dashboard `/`, `/jobs`,
  `/jobs/[id]`, `/pipeline`, fallback demo-data se API offline.
- **Infra**: `.github/workflows/ci.yml` (ruff+pytest / lint+build), `.gitignore`,
  `.env.example`, docker-compose opcional, docs (ARCHITECTURE/AUDIT_REPORT/DEPLOYMENT/
  HANDOFF/TECHNICAL_DECISIONS/TESTING), fixtures sintéticas `data/fixtures/*.json`.
- **Lacuna crítica p/ Signal Graph:** zero referências a Greenhouse/Lever — coletores
  são fixture-only (`example.org`). Sem roles, grafo de coocorrência ou portfolio gap.

### Decisão de recuperação (aprovada pelo autor)

Merge da branch em `feat/signal-graph` preservando histórico (reuse-first), seguido de
reestruturação `backend→apps/api`, `frontend→apps/web`. Conflitos esperados: README
(duplo rewrite) e `icon.png` (raiz ↔ `assets/`).

## Divergências repo/pack e resoluções

| Divergência | Resolução |
|---|---|
| Strandada usa `backend/`+`frontend/`; pack pede `apps/api`+`apps/web` | Pack prevalece via `git mv`; equivalência registrada aqui |
| Coletores fixture-only | Substituídos por adapters Greenhouse/Lever testados por fixtures |
| Dedup por título+empresa | Estendido para `source + source_job_id + text_hash` (contrato G3), mantendo fingerprint antigo como heurística auxiliar quando aplicável |
| Taxonomy sem evidence span | Estendida para retornar `SkillEvidence` (skill, confidence, evidence, method) |
| Sem roles/graph/gap/snapshot | Novos serviços conforme spec |
| requirements.txt | Migrado p/ `apps/api/pyproject.toml` (pack); pins equivalentes |

## Reuso

- **Mantido/adaptado:** normalizer (regex PT-BR), abordagem taxonomy dict+aliases,
  esqueleto de rotas FastAPI/UI Next.js, CI como base, fixtures sintéticas, .gitignore.
- **Substituído:** collectors fixture-only → adapters httpx GH/Lever.
- **Novo:** contracts Pydantic do spec, registry YAML, roles, graph (coocorrência+
  Jaccard+suporte mínimo), portfolio gap, build_snapshot.py, snapshot agregado público,
  UI trends/graph/bundles/gap, Playwright smoke enxuto.

## Riscos

- **P0** — nenhum conhecido no baseline.
- **P1** amostra pequena de boards GH/Lever BR (mitigada por disclaimers honestos);
  Playwright pode instabilizar CI (job isolado, degradação documentada); conflitos de merge.
- **P2** Node 24 local vs 20 CI (engines pinadas); scripts cross-platform p/ Windows.

## Plano de execução

Fases 0–17 do plano aprovado (recuperação → reestruturação → features TDD G1–G7 →
snapshot → UI → captura híbrida real → hardening → PR/merge → deploy Vercel →
publication gate → pacote LinkedIn fora do repo). TDD obrigatório; commits pequenos
convencionais; nenhum reset/history rewrite.
