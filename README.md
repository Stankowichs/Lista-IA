# Lista 1 de IA - AB2 2026.1

Repositório com as implementações da Lista 1 de Exercícios de Inteligência Artificial, referente à AB2 do período 2026.1.

**Instituição:** Universidade Federal de Alagoas  
**Disciplina:** Inteligência Artificial  
**Professor:** Evandro de Barros Costa  

## Integrantes

- Hugo Stankowich Souza
- Lucca Paes Costa
- Renato Coca Terrazas Freire
- Samuel Medino da Silva

## Visão Geral

O trabalho cobre três partes do enunciado:

1. Uma ferramenta genérica para construção de sistemas baseados em conhecimento.
2. Duas aplicações entre as opções propostas na lista.
3. Uma aplicação envolvendo agentes baseados em LLM.

As implementações desenvolvidas foram:

| Questão | Projeto | Descrição |
|---|---|---|
| 1 | `expert_shell/` | Shell genérica para sistemas especialistas, com regras de produção, inferência para frente, para trás e híbrida, explicações e base demonstrativa médica. |
| 2.1 | `akinator/` | Sistema de perguntas e respostas no estilo Akinator para identificar animais. |
| 2.4 | `cbr_medico/` | Sistema de diagnóstico médico educacional baseado em Raciocínio Baseado em Casos (CBR). |
| 3 | `agente_llm/` | Agente de triagem médica com LLM que usa o sistema CBR como ferramenta. |

> Todos os sistemas de domínio médico deste repositório têm finalidade exclusivamente educacional e não substituem avaliação profissional.

## Estrutura do Repositório

```text
.
├── Lista 1 de Exercícios de IA.pdf
├── Relatório Lista1 IA.pdf
├── expert_shell/
├── akinator/
├── cbr_medico/
└── agente_llm/
```

Cada subprojeto possui também seu próprio `README.md` e/ou `RELATORIO_TECNICO.md` com detalhes de arquitetura, implementação e exemplos.

## Pré-requisitos

- Python 3.10 ou superior
- Terminal com suporte a UTF-8
- Para o agente LLM: chave da Anthropic em `ANTHROPIC_API_KEY`

A maior parte dos projetos usa apenas a biblioteca padrão do Python. O projeto `agente_llm` depende do pacote `anthropic`.

## Como Executar

Execute cada projeto a partir da sua própria pasta.

### Questão 1 - Expert Shell

```bash
cd expert_shell
python main.py
```

A base demonstrativa `domains/medical.json` é carregada automaticamente.

### Questão 2.1 - Akinator de Animais

```bash
cd akinator
python main.py
```

O usuário pensa em um animal e responde às perguntas com `s`, `n` ou `ns`.

### Questão 2.4 - CBR Médico

```bash
cd cbr_medico
python main.py
```

O sistema coleta sintomas, recupera os casos mais semelhantes, sugere diagnóstico/tratamento e permite reter novos casos.

### Questão 3 - Agente LLM + CBR

Instale a dependência:

```bash
cd agente_llm
pip install -r requirements.txt
```

Defina a chave da API:

```bash
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

No Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY = "sua-chave-aqui"
```

Execute:

```bash
python main.py
```

O agente recebe sintomas em linguagem natural, chama ferramentas locais e consulta a base CBR do projeto `cbr_medico/`.

## Bases de Conhecimento

- `expert_shell/domains/medical.json`: base de regras médicas para a shell especialista.
- `akinator/knowledge_base.json`: animais, atributos e perguntas do Akinator.
- `cbr_medico/cases.json`: casos médicos fictícios usados pelo CBR e pelo agente LLM.

## Relatórios

O relatório consolidado está em:

```text
Relatório Lista1 IA.pdf
```

Os relatórios técnicos específicos estão em:

```text
expert_shell/RELATORIO_TECNICO.md
akinator/RELATORIO_TECNICO.md
cbr_medico/RELATORIO_TECNICO.md
agente_llm/RELATORIO_TECNICO.md
```

## Observações

- O repositório foi organizado para ser versionado como um único projeto.
- Os diretórios `.git` internos dos subprojetos foram removidos.
- Arquivos de cache, ambientes virtuais, `.DS_Store` e artefatos temporários são ignorados pelo `.gitignore` raiz.
