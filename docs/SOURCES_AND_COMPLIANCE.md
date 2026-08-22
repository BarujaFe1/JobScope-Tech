# Sources & Compliance

**Última validação:** 2026-08-22

## Fontes permitidas

Apenas APIs públicas e documentadas de ATS (Applicant Tracking System):

| ATS | Endpoint | Auth | Docs |
|---|---|---|---|
| Greenhouse Job Board | `GET /v1/boards/{token}/jobs?content=true` | pública, sem chave | developers.greenhouse.io/job-board.html |
| Lever Postings | `GET /v0/postings/{site}?mode=json` | pública, sem chave | github.com/lever/postings-api |

Nenhuma outra fonte entra no MVP. **Explicitamente fora de escopo:** LinkedIn,
scraping de HTML, APIs não documentadas, dados de candidatos.

## Comportamento do coletor

- somente `GET`; **nunca** chamamos endpoints de aplicação (`POST`);
- timeout configurável (default 30s) com retry exponencial limitado em 429/5xx;
- User-Agent default da lib httpx; volume baixo (1 request por board por captura);
- boards habilitados vivem em `data/config/sources.yml` com provenance da validação.

## Boards habilitados na captura atual

Validados ao vivo em 2026-08-22 (sondagem manual antes do enable):

| Empresa | ATS | Postings | Data/Analytics BR |
|---|---|---|---|
| Grupo QuintoAndar | Greenhouse | 90 | 9 |
| Agi (Banco Agibank) | Greenhouse | 177 | 15 |
| Airbnb | Greenhouse | 189 | 2 (escritório Brasil) |
| CI&T | Lever | 169 | 29 |

## O que armazenamos

- **No Git:** apenas agregados (`data/public/market_snapshot.json`) — frequências,
  arestas de grafo, snippets ≤200 chars com link para a vaga original;
- **Fora do Git:** raw cache completo (`data/raw/`, `data/cache/` — `.gitignore`);

## PII & direitos

- descrições de vagas são conteúdo público publicado pelas próprias empresas
  explicitamente para visualização de terceiros ("All published job postings…
  may be scraped by third parties" — Lever README);
- não armazenamos nomes, e-mails ou qualquer dado de candidato;
- nenhum dado pessoal/financeiro/fiscal entra no snapshot público;
- remoção: basta desabilitar o board no registry e rebuildar o snapshot.

## Limitações declaradas

- a amostra = apenas os boards habilitados; **não representa todo o mercado
  brasileiro** (a maioria das empresas BR usa Gupy/Own, que estão fora do escopo);
- empresas multinationais contribuem apenas vagas de escritórios BR quando
  identificáveis pelo campo location.
