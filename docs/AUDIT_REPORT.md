# Audit Report — JobScope Tech BR

**Data:** 2026-07-13  
**Branch:** `chore/portfolio-quality-pass`  
**Repositório:** `BarujaFe1/JobScope-Tech`

---

## Resumo executivo

O repositório era, na prática, um **README de produto sem código**. Existiam narrativa forte, escopo V1 bem definido, arquitetura planejada e um ícone — mas **zero implementação** (backend, frontend, pipeline, testes, CI, `.env.example`, Docker).

Isso cria um risco grave de portfólio: um recrutador abre o repo, vê um README ambicioso e descobre que nada roda. A nota cai por credibilidade, não por falta de ideia.

A proposta do produto (data product de vagas tech BR: coleta → parse → normalização → taxonomia → dedup → API → dashboard) é clara e defensável. O trabalho deste pass transforma a especificação em uma **V1 demo executável**, com seed data, API FastAPI, dashboard Next.js, testes, CI e documentação honesta.

---

## Nota atual (pré-pass)

| Critério | Nota | Comentário |
|---|---:|---|
| Clareza da tese | 8/10 | README excelente em narrativa |
| Código / executabilidade | 0/10 | Sem código |
| DX (rodar local) | 0/10 | Quick start aponta para estrutura inexistente |
| Testes | 0/10 | Ausentes |
| Segurança | 5/10 | Sem secrets, mas sem `.gitignore` útil |
| UX / demo | 0/10 | Sem UI |
| Documentação técnica | 3/10 | Só README; docs/ inexistente |
| Valor de portfólio | 2/10 | Ideia forte, entrega vazia |

**Nota geral pré-pass: 2.5 / 10**

---

## Principais riscos

1. **Credibilidade:** README promete stack e estrutura que não existem.
2. **Clone URL inconsistente:** README cita `jobscope-tech-br`; o repo real é `JobScope-Tech`.
3. **Scraping de fontes reais:** risco legal/ToS se coletores vivos forem adicionados sem cuidado.
4. **Escopo inflado:** tentação de LLM/NLP/auth antes de fechar V1.
5. **Deploy inexistente:** sem build, sem demo pública.
6. **Ícone 1.6MB na raiz:** asset pesado sem otimização.

---

## Quick wins

- Criar estrutura real alinhada ao README.
- Seed/demo data (sem scraping ao vivo na V1).
- API mínima com `/health`, `/jobs`, `/stats`, `/skills`, `/pipeline/status`.
- Dashboard Next.js consumindo a API (ou fallback demo).
- `.gitignore`, `.env.example`, CI, docs técnicas.
- README honesto: o que roda hoje vs roadmap.

---

## Melhorias estruturais

- Separar `backend/` (domínio + API + pipeline) e `frontend/` (Next.js).
- SQLite por padrão para demo zero-friction; Postgres via Docker Compose opcional.
- Domínio puro (normalizer, taxonomy, dedup) testável sem HTTP.
- Fixtures JSON como “fontes” V1 (coletores reais documentados como próximo passo).
- Scripts: seed, pipeline run, health check.

---

## Bugs encontrados (estado inicial)

| ID | Severidade | Descrição |
|---|---|---|
| B01 | Crítico | Nenhuma aplicação para instalar/rodar |
| B02 | Alto | Quick Start documenta paths/comandos inexistentes |
| B03 | Alto | Estrutura de pastas do README não existe |
| B04 | Médio | Nome do repo vs clone URL divergentes |
| B05 | Baixo | `icon.png` ~1.6MB sem versão otimizada |
| B06 | Baixo | Sem `.gitignore` (risco futuro de `.env`/venv) |

---

## Plano de execução

1. Branch `chore/portfolio-quality-pass`.
2. Scaffold monorepo + configs de qualidade.
3. Implementar backend FastAPI + domínio + seed + pytest.
4. Implementar frontend Next.js (dashboard, lista, detalhe).
5. Docker Compose (Postgres opcional) + CI.
6. Docs: ARCHITECTURE, TECHNICAL_DECISIONS, TESTING, DEPLOYMENT, HANDOFF.
7. README de portfólio reescrito com status real.
8. Rodar install/lint/test/build; commit e push.

---

## Checklist final (aceitação)

- [x] Projeto instala
- [x] Projeto roda (seed + API + UI; fixtures documentadas)
- [x] Build passa (`npm run build`, pytest, ruff)
- [x] Bugs principais corrigidos / registrados
- [x] README forte e honesto
- [x] Docs criadas
- [x] CI adicionada
- [x] `.env.example` presente
- [x] `.gitignore` protege sensíveis
- [x] Testes essenciais existem
- [x] UX revisada na demo
- [x] `docs/HANDOFF.md` completo

**Nota pós-pass (estimada): ~7.5 / 10** — demo runnable, docs e CI sólidos; faltam screenshots reais, deploy público e coletor vivo.
