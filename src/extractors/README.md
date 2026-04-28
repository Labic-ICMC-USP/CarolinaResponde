# Pipeline de extração

A extração de documentos utiliza a biblioteca [Docling](https://github.com/docling-project/docling) com o pipeline padrão:

- **DocLayNet** para detecção de layout
- **TableFormer** (modo `ACCURATE`) para extração de tabelas
- **EasyOCR** (pt-BR + en) para reconhecimento de texto

A saída é um JSON por documento em `extracted_data/`, com um registro por página contendo o texto extraído em markdown.

## Dependências externas

Arquivos `.docx` são convertidos para PDF via [pandoc](https://pandoc.org/) antes da extração. O pandoc requer um motor LaTeX para gerar PDFs.

### Pandoc e LaTeX

#### Windows (PowerShell)

```powershell
winget install --id JohnMacFarlane.Pandoc
winget install --id MiKTeX.MiKTeX
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install pandoc texlive-latex-recommended texlive-fonts-recommended
```

### Verificar instalação

```bash
pandoc --version
pdflatex --version
```
