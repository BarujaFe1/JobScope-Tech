# Security Notes

**Data:** 2026-07-13  
**Branch:** `chore/portfolio-quality-pass`

## Achados

Nenhum segredo, token, chave de API ou credencial foi encontrado no histórico inicial do repositório (README + LICENSE + ícone).

## Proteções adicionadas

- `.gitignore` cobre `.env`, virtualenvs, `node_modules`, bancos locais e artefatos de build.
- `.env.example` documenta variáveis sem valores sensíveis.
- Fontes V1 são fixtures sintéticas (sem scraping de dados pessoais reais).

## Boas práticas daqui pra frente

1. Nunca commitar `.env` ou dumps de banco.
2. Se adicionar coletores reais, respeitar ToS/robots e evitar armazenar PII desnecessária.
3. Se um segredo vazar: rotacionar imediatamente, remover do histórico se necessário, e registrar aqui **sem republicar o valor**.
