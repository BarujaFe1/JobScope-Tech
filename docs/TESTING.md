# Testing — JobScope Tech BR

## Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
ruff check app tests scripts
pytest -q
```

### O que cobrimos

| Suite | Foco |
|---|---|
| `tests/test_domain.py` | Senioridade, modalidade, skills, fingerprint |
| `tests/test_api.py` | Health, stats, filtros, detalhe, pipeline, dedup cross-board |

### Notas

- API tests usam SQLite in-memory + override de `get_db`.
- `JOBSCOPE_DEMO_MODE=false` evita seed do lifespan no engine “real” durante testes.

## Frontend

```bash
cd frontend
npm ci
npm run lint
npm run build
```

Não há suite de componente ainda; CI valida lint + build de produção.

## Como adicionar testes

1. Domínio puro → `tests/test_domain.py` (preferido).
2. Contrato HTTP → `tests/test_api.py` com fixture `client`.
3. Novo parser → fixture JSON + assert de campos canônicos.
