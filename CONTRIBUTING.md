# Contributing

Issues e PRs são bem-vindos, especialmente em:

- qualidade de parsers
- taxonomia de skills
- deduplicação
- UX do dashboard
- documentação

## Fluxo

```bash
git checkout -b feature/sua-ideia
# ... mudanças + testes ...
git commit -m "feat: descreva o porquê"
git push origin feature/sua-ideia
```

Abra um Pull Request contra `main`.

## Checklist

- [ ] `pytest` passa no backend
- [ ] `ruff check` limpo
- [ ] `npm run lint` + `npm run build` no frontend (se UI mudou)
- [ ] Sem `.env` / secrets no commit
