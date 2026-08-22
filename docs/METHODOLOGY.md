# Methodology — JobScope Signal Graph

**Methodology version:** 1.0.0 (registrada em cada snapshot em `meta.methodology_version`)

## Pipeline

```
sources.yml (boards habilitados)
  → adapters (Greenhouse/Lever, GET público, retry/backoff)
  → NormalizedJob (source, id, company, title, location, url,
                   captured_at ← payload, text_hash = sha256(texto canônico))
  → dedup (G3): mesma (source,id) mantém captured_at mais recente;
               text_hash igual entre fontes colapsa e preserva duplicate_of
  → skills: dicionário versionado (skills.yml) com aliases; cada detecção
            retorna SkillEvidence(skill, confidence=1.0, evidence=span ±60 chars, method=dictionary)
  → roles: regras ordenadas transparentes (PT-BR+EN) com razão + termo que disparou
  → grafo por role: aresta só se par coocorrer em ≥ min_support vagas;
                    métricas suporte absoluto + Jaccard
  → portfolio gap: compara frequência de mercado vs evidence.yml (apenas registro manual)
  → market_snapshot.json (agregados públicos)
```

## Decisões semânticas documentadas

| Parâmetro | Valor | Por quê |
|---|---|---|
| `min_support` | 2 | pares com 1 coocorrência são ruído; abaixo disso a aresta nem existe |
| `demand_threshold` (gap) | 5 | skill precisa aparecer em ≥5 vagas para virar "demanda" |
| hash de texto | sha256 de whitespace-canônico | mesmo texto com quebras diferentes = mesma vaga |
| `captured_at` | do payload (`updated_at`/`createdAt`) | determinístico/reprodutível, não "hora da coleta" |
| LLM | ausente nesta versão | gates determinísticos não dependem de chave; hook futuro opcional |

## Golden scenarios (contratos testados)

1. **G1** fixture Greenhouse normaliza estável → `tests/test_adapter_greenhouse.py`
2. **G2** fixture Lever normaliza para o MESMO contract → `tests/test_adapter_lever.py`
3. **G3** dedup source+id/hash no snapshot → `tests/test_snapshot_storage.py`
4. **G4** alias `postgresql→PostgreSQL` **com evidence span** → `tests/test_skills.py`
5. **G5** sem LLM/key o pipeline segue funcional → `tests/test_skills.py`
6. **G6** aresta abaixo do suporte mínimo é excluída → `tests/test_graph.py`
7. **G7** gap usa SOMENTE evidência explicitamente registrada → `tests/test_portfolio_gap.py`

## Como reproduzir

```bash
# snapshot sintético (determinístico, fixtures commitadas):
python scripts/build_snapshot.py --mode synthetic

# snapshot real (respeita sources.yml habilitado):
python scripts/build_snapshot.py --mode live

cd apps/api && pytest -q        # 69 testes, incluindo os 7 golden scenarios
```

## Limitações honestas

1. Amostra ≠ mercado: apenas boards Greenhouse/Lever habilitados; Gupy (dominante no BR) está fora.
2. Extração por dicionário tem recall limitado — skill não listada simplesmente não aparece.
3. Role normalization é baseada em título (+ descrição como fallback); títulos ambíguos caem em `other`.
4. Snapshot é um corte temporal; trends longitudinais exigem múltiplas capturas (estrutura já preparada via `generated_at`).
5. Jaccard não implica causalidade — coocorrência descreve demanda conjunta observada.
