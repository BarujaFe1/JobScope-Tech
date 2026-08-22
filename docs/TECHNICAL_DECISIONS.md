# Technical Decisions — JobScope Tech BR

## 1. Fixtures primeiro, scraping depois

**Decisão:** V1 alimenta o pipeline com JSON fixtures, não com scrapers vivos.

**Por quê:** Scraping de boards é instável, sensível a ToS e ruim para CI. Fixtures provam o pipeline end-to-end e são fáceis de testar.

**Trade-off:** Demo não mostra coleta “ao vivo”. Mitigado documentando o contrato do coletor.

## 2. SQLite default, Postgres opcional

**Decisão:** Demo local usa SQLite; Postgres via Docker Compose.

**Por quê:** Reduz barreira de entrada para recrutadores clonarem o repo.

**Trade-off:** Algumas features SQL avançadas ficam para depois. Aceitável na V1.

## 3. Taxonomia por dicionário (sem LLM)

**Decisão:** Skills via aliases + regex.

**Por quê:** Explicável, barato, testável, alinhado ao escopo do README.

**Trade-off:** Falsos positivos/negativos. Transparência > magia.

## 4. Dedup pragmático por fingerprint

**Decisão:** Hash de título + empresa normalizados.

**Por quê:** Impede republicação óbvia entre boards (provado no seed com NuvemPay).

**Trade-off:** Não resolve títulos divergentes da mesma vaga. Suficiente para V1.

## 5. Frontend com fallback demo

**Decisão:** UI degrada para snapshot se API cair.

**Por quê:** Preview de portfólio na Vercel sem obrigar backend no ar.

**Trade-off:** Snapshot pode divergir do seed. Aceitável se documentado.

## 6. Sem Alembic na V1

**Decisão:** `create_all` no startup.

**Por quê:** Menos pieces móveis para uma demo. Schema ainda é simples.

**Trade-off:** Migrações reais entram quando o schema estabilizar.
