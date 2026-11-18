# Assistente de Suporte de TI (RAG)

Assistente que responde dúvidas de suporte de TI com base em documentos internos
(manuais, procedimentos, FAQs), **sempre citando os trechos usados**.

- **Back-end:** Python 3.12 + FastAPI + ChromaDB (em `backend/`)
- **Front-end:** React + Vite + TypeScript (em `frontend/`)
- **Documentos de exemplo:** `docs-exemplo/` (Markdown/TXT; PDF numa etapa posterior)

## Forma de trabalho

- O projeto avança **uma etapa por vez**, seguindo o plano combinado. Não adiantar
  trabalho de etapas futuras.
- Toda etapa termina com **testes passando** e um resumo do que mudou.
- **Quem faz commit é o usuário.** Não rodar `git commit`/`git push`; ao fim da etapa,
  sugerir uma mensagem de commit no padrão Conventional Commits em português
  (ex.: `feat(backend): adiciona endpoint de ingestão`).
- Mudanças pequenas e revisáveis; evitar dependências novas sem justificar.

## Estrutura

```
backend/
  app/
    main.py          # cria o app FastAPI e registra as rotas
    config.py        # configurações via variáveis de ambiente (pydantic-settings)
    api/             # rotas (finas: validam entrada e delegam aos serviços)
    rag/             # ingestão, chunking, embeddings, busca, montagem do prompt
    llm/             # interface do provedor de LLM + implementações
    models.py        # schemas Pydantic de request/response
  tests/
  pyproject.toml
frontend/
  src/
    components/
    api/             # cliente HTTP do back-end
  ...
docs-exemplo/
```

## Convenções — Back-end

- Ambiente: `python -m venv .venv` dentro de `backend/`; dependências no `pyproject.toml`.
- Lint/format: `ruff check .` e `ruff format .`. Type hints em todo código novo.
- Testes: `pytest` (rodar de dentro de `backend/`). Usar `TestClient` do FastAPI.
- **Testes nunca chamam LLM real nem baixam modelos**: usar o provedor falso
  (`FakeLLM`) e embeddings falsos/determinísticos; ChromaDB em diretório temporário.
- Configuração só via variáveis de ambiente / `.env` (nunca commitar `.env`;
  manter `.env.example` atualizado).
- Rotas finas; regra de negócio em `rag/` e `llm/`. Dependências injetadas via
  `Depends` para facilitar testes.
- Código e identificadores em inglês; mensagens ao usuário e docs em português.

## Convenções — RAG e citações

- Cada chunk guarda metadados: `doc_id`, `source` (nome do arquivo), `title`/seção,
  `chunk_index`.
- O prompt numera os trechos recuperados (`[1]`, `[2]`, …) e instrui o modelo a
  citar com esses marcadores e a dizer que não sabe quando os trechos não cobrirem
  a pergunta.
- A resposta da API sempre traz `answer` + `sources` (lista com `id`, `source`,
  `excerpt`, `score`). O front-end exibe os marcadores clicáveis ligados aos trechos.
- Ids de chunk determinísticos (hash de arquivo + índice) para reingestão idempotente.

## Convenções — Front-end

- TypeScript estrito; componentes funcionais com hooks.
- Testes: Vitest + React Testing Library (`npm test`). Lint: `npm run lint`.
- URL da API via `VITE_API_URL`. Sem bibliotecas de UI pesadas; CSS simples
  (CSS Modules ou um arquivo de estilos por componente).

## Comandos

```bash
# back-end
cd backend && source .venv/bin/activate
pytest
ruff check . && ruff format --check .
uvicorn app.main:app --reload

# front-end
cd frontend
npm test
npm run lint
npm run dev
```
