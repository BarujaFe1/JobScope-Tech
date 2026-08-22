# Deployment — JobScope Tech BR

## Local (recomendado para demo)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3000

### Postgres opcional

```bash
docker compose up -d
# no .env:
# DATABASE_URL=postgresql+psycopg://jobscope:jobscope@localhost:5432/jobscope
# (instale psycopg[binary] se for usar Postgres)
```

## Frontend na Vercel

1. Root directory: `frontend`
2. Env:
   - `NEXT_PUBLIC_API_URL` → URL pública do backend (Railway etc.)
   - `NEXT_PUBLIC_DEMO_MODE=true` → fallback se API estiver offline
3. Build command: `npm run build`

Sem backend no ar, a UI ainda abre em modo demo.

## Backend (Railway / similar)

1. Root: `backend`
2. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Env: `DATABASE_URL`, `CORS_ORIGINS`, `JOBSCOPE_DEMO_MODE=true`
4. Rodar seed no release: `python scripts/seed.py`

## Ainda não feito

- Deploy público permanente com domínio
- Alembic migrations
- Coletores reais em produção
- Screenshots/vídeo demo no README
