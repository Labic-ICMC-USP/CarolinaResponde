# FAQ Generator

Gera pares de pergunta-e-resposta (QA) a partir dos chunks produzidos pelo [`chunker/`](../chunker/), usando um LLM via [OpenRouter](https://openrouter.ai/).

## Como funciona

Para cada chunk de cada documento:

1. O template em [`prompts/faq_generation.txt`](../../prompts/faq_generation.txt) é preenchido com o texto do chunk e o número de perguntas desejado.
2. O prompt é enviado a um único modelo configurado em `config.yaml`.
3. A resposta deve ser um array JSON puro (sem markdown, sem comentários). É feito o parse e cada item é validado.
4. Itens inválidos são descartados; itens válidos são acumulados como `qa_pairs` daquele chunk.

## Validação dos pares

Um par é aceito apenas se:

- `question` é string não-vazia
- `answer` é string não-vazia
- `source_page` é um inteiro presente em `chunk.pages`

A última checagem evita que o modelo "invente" páginas fora do chunk, garantindo rastreabilidade.

## Configuração

Em `config.yaml`:

```yaml
llm:
  faq_generator:
    provider: openrouter
    model: google/gemma-4-31b-it
    temperature: 0.0
    api_key_env: OPENROUTER_API_KEY

faq_generation:
  questions_per_chunk: 10
```

A chave de API deve estar em `.env`:

```
OPENROUTER_API_KEY=sk-or-...
```

## Entrada

Arquivos em `chunked_data/<subpasta>/<doc>.json` (saída do chunker).

## Saída

Arquivos em `faq_data/<subpasta>/<doc>.json`, espelhando a estrutura de `chunked_data/`. Idêntica à entrada, com `qa_pairs` adicionado a cada chunk:

```json
{
  "doc_name": "...",
  "source_path": "...",
  "chunks": [
    {
      "chunk_id": "doc_name__c0",
      "pages": [1, 2],
      "chunk_text": "...",
      "qa_pairs": [
        {"question": "...", "answer": "...", "source_page": 1},
        ...
      ]
    },
    ...
  ]
}
```

## Comandos

```bash
# todos os documentos chunkados
python -m faq_generator.run_faq_generation chunked_data

# uma pasta específica
python -m faq_generator.run_faq_generation chunked_data/PPC

# um único arquivo
python -m faq_generator.run_faq_generation "chunked_data/PPC/PPC - Bacharelado em Ciências de Computação (BCC) 2026-1.json"

# sobrescrever saídas já existentes
python -m faq_generator.run_faq_generation chunked_data --force
```

Por padrão, documentos já gerados são **pulados**. Use `--force` para regenerar.
