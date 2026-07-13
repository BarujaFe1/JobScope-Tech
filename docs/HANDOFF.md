# Handoff — JobScope Tech BR

**Branch:** `chore/portfolio-quality-pass`  
**Data:** 2026-07-13  
**Autor da revisão:** Cursor agent (portfolio quality pass)

---

## O que foi encontrado

O repositório era **README + LICENSE + ícone** (~1.6MB). Narrativa de produto excelente, mas:

- nenhuma pasta `backend/` / `frontend/` / `docs/`
- quick start apontava para estrutura inexistente
- clone URL no README antigo divergia do nome real do repo
- zero testes, CI, `.env.example` ou `.gitignore` útil
- risco alto de credibilidade para recrutadores

Nota pré-pass: **~2.5/10** (ver `docs/AUDIT_REPORT.md`).

---

## O que foi corrigido / criado

### Produto executável

- Backend FastAPI com models, schemas, services, pipeline
- Domínio testável: normalizer, taxonomy, dedup
- 2 fontes fixture (`fixture_board_a`, `fixture_board_b`) + seed
- Dedup cross-board comprovado (vaga NuvemPay duplicada é skipped)
- Auto-seed no startup em demo mode se DB vazio
- Frontend Next.js: Dashboard, Vagas (filtros), Detalhe, Pipeline
- Fallback demo na UI quando a API está offline

### Qualidade pública

- `.gitignore`, `.env.example`, `SECURITY_NOTES.md`
- `docker-compose.yml` (Postgres opcional)
- CI GitHub Actions (ruff + pytest + lint + build)
- Docs: ARCHITECTURE, TECHNICAL_DECISIONS, TESTING, DEPLOYMENT, AUDIT, HANDOFF
- README reescrito como peça de portfólio (honesto sobre status)

---

## Comandos rodados

```bash
git checkout -b chore/portfolio-quality-pass

# Backend
cd backend
python -m venv .venv
pip install -r requirements.txt
ruff check app tests scripts
pytest -q          # 10 passed
python scripts/seed.py

# Frontend
cd frontend
npm install
npm run lint       # clean
npm run build      # success
```

---

## Testes executados

| Suite | Resultado |
|---|---|
| `pytest` (domain + API) | **10 passed** |
| `ruff check` | **All checks passed** |
| `npm run lint` | **No warnings/errors** |
| `npm run build` | **Success** (/, /jobs, /jobs/[id], /pipeline) |

---

## O que ainda falta

1. Screenshots reais + vídeo curto de demo
2. Deploy público (Vercel frontend + Railway backend)
3. Coletor real (com cuidado de ToS) no lugar das fixtures
4. Alembic migrations quando o schema estabilizar
5. Otimizar `assets/icon.png` (ainda ~1.6MB)
6. Testes de componente no frontend (opcional)
7. Atualizar descrição do repositório no GitHub

---

## Riscos restantes

- Fixtures ≠ coleta ao vivo (documentado de propósito)
- Taxonomia por dicionário tem falsos positivos/negativos
- Dedup não cobre títulos muito diferentes da mesma vaga
- Sem auth (ok para V1 pública read-only)
- Ícone pesado pode afetar clone/LCP se usado sem otimizar

---

## Próximos passos sugeridos

1. Push desta branch e abrir PR para `main`
2. Deploy frontend na Vercel com `NEXT_PUBLIC_DEMO_MODE=true`
3. Capturar screenshots e substituir o placeholder SVG
4. Adicionar um coletor real de uma fonte estável/permitida
5. Atualizar a descrição do repo no GitHub para a tagline do README

---

## Sugestões para o portfólio

- Colocar JobScope como **case de data product end-to-end**
- Na entrevista: enfatizar o que **não** entrou no escopo (disciplina)
- Mostrar o teste de dedup e o `/docs` da API ao vivo
- Linkar `docs/TECHNICAL_DECISIONS.md` no case study

---

## Mensagem de commit sugerida

```txt
chore: improve portfolio quality, docs, tests and stability
```

(Usada neste pass conforme brief.)
