# CarolinaResponde

Agente conversacional para responder dúvidas de usuários com base em documentos públicos do ICMC-USP.

## Sobre o projeto

O objetivo é criar um agente conversacional que auxilie alunos, professores e funcionários a encontrar informações sobre portarias, regulamentações institucionais e procedimentos da graduação — conteúdos que costumam estar espalhados em vários documentos com linguagem formal e pouco direta.

O agente utiliza uma abordagem de **RAG-FAQ**, na qual os documentos são pré-processados no formato de perguntas e respostas. Isso permite que o agente recupere trechos mais relevantes e gere respostas objetivas com referências.

Este projeto utiliza o [RAG-FAQ](https://github.com/Labic-ICMC-USP/llm4gov/tree/main/rag_faq) como motor de recuperação e geração de respostas.

## Base de conhecimento

Os documentos que compõem a base de conhecimento do agente são:

| Fonte | Descrição
|---|---|
| `Manual SVGRAD` | Procedimentos e orientações da Secretaria de Graduação |
| `PPC` | Projetos Pedagógicos dos Cursos de graduação do ICMC |
| `Regimento CoCs ICMC` | Regimentos das Comissões de Cursos do ICMC |

## Estrutura do repositório

```
CarolinaResponde/
└── README.md
```
