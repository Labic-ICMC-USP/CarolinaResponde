# CarolinaResponde

Agente conversacional para responder dúvidas de usuários com base em documentos públicos do ICMC-USP.

## Sobre o projeto

O objetivo é criar um agente conversacional que auxilie alunos, professores e funcionários a encontrar informações sobre portarias, regulamentações institucionais e procedimentos da graduação — conteúdos que costumam estar espalhados em vários documentos com linguagem formal e pouco direta.

O agente utiliza uma abordagem de **RAG-FAQ**, na qual os documentos são pré-processados no formato de perguntas e respostas. Isso permite que o agente recupere trechos mais relevantes e gere respostas objetivas com referências.

Este projeto utiliza o [RAG-FAQ](https://github.com/Labic-ICMC-USP/llm4gov/tree/main/rag_faq) como motor de recuperação e geração de respostas.

## Base de conhecimento

Os documentos que compõem a base de conhecimento do agente são:

| Fonte | Descrição |
|---|---|
| `Manual SVGRAD` | Procedimentos e orientações da Secretaria de Graduação |
| `PPC` | Projetos Pedagógicos dos Cursos de graduação do ICMC |
| `Regimento CoCs ICMC` | Regimentos das Comissões de Cursos do ICMC |

## Pipeline

O pré-processamento dos documentos é dividido em etapas independentes, cada uma lendo a saída da anterior:

```
data/              →  extracted_data/  →  chunked_data/  →  faq_data/   →  faq_eval/
(documentos          (uma página            (chunks com       (chunks         (planilhas
 originais)           por registro)          sobreposição)     com QA)         para revisão)
```

| Etapa | Módulo | Documentação |
|---|---|---|
| Extração | `src/extractors/` | [README](src/extractors/README.md) |
| Chunking | `src/chunker/` | [README](src/chunker/README.md) |
| Geração de FAQ | `src/faq_generator/` | [README](src/faq_generator/README.md) |

## Estrutura do repositório

```
CarolinaResponde/
├── data/                                 # documentos fonte
├── extracted_data/                       # saída da extração (gitignored)
├── chunked_data/                         # saída do chunking (gitignored)
├── faq_data/                             # saída da geração de FAQ (gitignored)
├── faq_eval/                             # planilhas de avaliação (gitignored)
├── prompts/
│   └── faq_generation.txt                # template do prompt do gerador de FAQ
├── src/
│   ├── extractors/                       # extração de PDF/DOCX via Docling
│   │   ├── __init__.py
│   │   ├── schema.py                     # PageRecord
│   │   ├── pdf.py
│   │   ├── docx.py
│   │   ├── run_extraction.py             # CLI
│   │   └── README.md
│   ├── chunker/                          # sliding-window chunker
│   │   ├── __init__.py
│   │   ├── schema.py                     # Chunk
│   │   ├── chunker.py
│   │   ├── run_chunking.py               # CLI
│   │   └── README.md
│   ├── faq_generator/                    # gera QA via OpenRouter
│   │   ├── __init__.py
│   │   ├── schema.py                     # QAPair, ChunkWithFAQs
│   │   ├── client.py
│   │   ├── prompt.py
│   │   ├── generator.py
│   │   ├── run_faq_generation.py         # CLI
│   │   └── README.md
│   └── shared/
│       └── utils.py
├── scripts/
│   └── export_faq_xlsx.py                # exporta faq_data → planilhas xlsx
├── config.yaml                           # parâmetros do pipeline
├── requirements.txt
└── pyproject.toml
```

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell)
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
pip install -e .
```

A etapa de extração possui dependências externas (pandoc + LaTeX para arquivos `.docx`) — veja [`src/extractors/README.md`](src/extractors/README.md).

## Configuração

Parâmetros do pipeline ficam em [`config.yaml`](config.yaml).

## Uso

Cada etapa é executada como um módulo Python a partir da raiz do repositório.

### 1. Extração

```bash
python -m extractors.run_extraction data
```

Detalhes em [`src/extractors/README.md`](src/extractors/README.md).

### 2. Chunking

```bash
python -m chunker.run_chunking extracted_data
```

Detalhes em [`src/chunker/README.md`](src/chunker/README.md).

### 3. Geração de FAQ

```bash
python -m faq_generator.run_faq_generation chunked_data
```

Detalhes em [`src/faq_generator/README.md`](src/faq_generator/README.md).

### 4. Exportação para avaliação humana

Para que pessoas possam revisar os pares de pergunta-resposta gerados, há um script auxiliar que lê os JSONs de `faq_data/` e exporta uma planilha XLSX por documento, espelhando a estrutura de pastas em `faq_eval/`:

```bash
# todos os documentos
python scripts/export_faq_xlsx.py faq_data

# uma pasta específica
python scripts/export_faq_xlsx.py faq_data/PPC

# um único arquivo
python scripts/export_faq_xlsx.py "faq_data/PPC/PPC - Bacharelado em Ciências de Computação (BCC) 2026-1.json"

# sobrescrever planilhas já existentes
python scripts/export_faq_xlsx.py faq_data --force
```

Cada planilha tem uma linha por par QA, ordenada por `source_page`, com as colunas: `chunk_pages`, `source_page`, `question`, `answer`. A ideia é que o revisor abra a planilha lado a lado com o documento original e verifique se cada par é correto, coerente e fiel à fonte.
