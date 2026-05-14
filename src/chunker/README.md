# Chunker

Particiona os JSONs gerados pelo [`extractors/`](../extractors/) em **trechos sobrepostos** (sliding window) que servirão de entrada para a geração de FAQ.

## Como funciona

Cada documento extraído é uma lista de páginas. O chunker desliza uma janela de tamanho `window_size` páginas com sobreposição `overlap` páginas entre janelas consecutivas. Isso preserva contexto entre páginas e evita cortar conteúdo no meio de uma seção.

O texto de cada chunk embute marcadores `[Página N]` antes do texto de cada página, de modo que o gerador de FAQ saiba a qual página pertence cada trecho ao atribuir `source_page` a uma pergunta.

Casos de borda:

- Documento com 1 página → 1 chunk com aquela página.
- Documento menor que `window_size` → 1 chunk com todas as páginas.
- Última janela menor que `window_size` → mantida (não preenchida).

## Configuração

Em `config.yaml`:

```yaml
chunking:
  window_size: 2   # número de páginas por chunk
  overlap: 1       # páginas compartilhadas entre chunks consecutivos
```

Restrições: `window_size >= 1` e `0 <= overlap < window_size`.

## Entrada

Arquivos em `extracted_data/<subpasta>/<doc>.json`, com o esquema de saída do extrator (lista de `PageRecord`s):

```json
[
  {"doc_name": "...", "source_path": "...", "page": 1, "page_count": 12, "text": "..."},
  ...
]
```

## Saída

Arquivos em `chunked_data/<subpasta>/<doc>.json`, espelhando a estrutura de pastas de `extracted_data/`:

```json
{
  "doc_name": "...",
  "source_path": "...",
  "chunks": [
    {
      "chunk_id": "doc_name__c0",
      "pages": [1, 2],
      "chunk_text": "[Página 1]\n...\n\n[Página 2]\n..."
    },
    ...
  ]
}
```

## Comandos

```bash
# todos os documentos extraídos
python -m chunker.run_chunking extracted_data

# uma pasta específica
python -m chunker.run_chunking extracted_data/PPC

# um único arquivo
python -m chunker.run_chunking "extracted_data/PPC/PPC - Bacharelado em Ciências de Computação (BCC) 2026-1.json"
```
