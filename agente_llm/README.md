# Agente de Triagem Médica — LLM + CBR

Agente conversacional que recebe descrições de sintomas em linguagem natural, consulta uma base de casos médicos via **Raciocínio Baseado em Casos (CBR)** e explica o diagnóstico usando o modelo de linguagem **Claude (Anthropic)**.

**Disciplina:** Inteligência Artificial — AB2 2026.1  
**Professor:** Evandro Costa — UFAL  
**Questão:** 3 — Aplicação envolvendo agentes baseados em LLM (2 pts)

> ⚠️ Ferramenta **exclusivamente educacional**. Não substitui diagnóstico médico profissional.

---

## Como funciona

```
Usuário descreve sintomas em português
        ↓
Claude chama list_symptoms → conhece os 20 sintomas do sistema
        ↓
Claude chama search_medical_cases → CBR retorna top-3 casos por cosseno
        ↓
Claude interpreta e explica o diagnóstico em linguagem natural
```

O agente decide autonomamente quando e quais ferramentas chamar. O histórico completo da conversa é mantido a cada turno (memória multi-turno).

---

## Pré-requisitos

- Python 3.10+
- Chave de API da Anthropic: [console.anthropic.com](https://console.anthropic.com)
- Pasta `../cbr_medico/` com `cbr_engine.py` e `cases.json` (Questão 2.4)

### Instalar dependências

```bash
pip install anthropic>=0.112.0
```

---

## Como executar

```bash
# 1. Definir a API key
set ANTHROPIC_API_KEY=sk-ant-...        # Windows
export ANTHROPIC_API_KEY=sk-ant-...     # Linux / macOS

# 2. Entrar na pasta e rodar
cd agente_llm
python main.py
```

---

## Exemplo de sessão

```
╔══════════════════════════════════════════════════════════════╗
║          AGENTE DE TRIAGEM MÉDICA  —  LLM + CBR              ║
║  Modelo : claude-opus-4-8                                    ║
║  Disciplina : IA — AB2 2026.1 — Prof. Evandro Costa — UFAL  ║
╚══════════════════════════════════════════════════════════════╝

Você: Estou com febre alta, perdi o olfato e tenho dificuldade para respirar.

  [ferramenta: list_symptoms]
  [ferramenta: search_medical_cases]

Agente: Com base nos seus sintomas — febre, perda de olfato e dificuldade
respiratória — o sistema identificou alta similaridade (75,6%) com casos
de COVID-19.

Diagnóstico mais provável: COVID-19
Tratamento sugerido: Isolamento por 10 dias, monitorar saturação de O₂,
antitérmicos; suporte médico se SpO₂ < 94%.

Diagnósticos diferenciais:
• Gripe (Influenza) — 62,1%
• Pneumonia Bacteriana — 58,4%

⚠️ Este é um sistema educacional. Consulte um médico para avaliação definitiva.
```

---

## Ferramentas do agente

| Ferramenta | Descrição |
|---|---|
| `list_symptoms` | Retorna os 20 sintomas rastreados na base de casos |
| `search_medical_cases` | Busca os 3 casos mais similares por similaridade de cosseno |

### Base de conhecimento (CBR)

17 casos clínicos, 7 diagnósticos possíveis:

| Diagnóstico | Casos |
|---|---|
| Gripe (Influenza) | C001, C002 |
| COVID-19 | C003, C004 |
| Dengue | C005, C006, C015 |
| Pneumonia Bacteriana | C007, C008, C016 |
| Malária | C009, C010 |
| Resfriado Comum | C011, C012, C017 |
| Gastroenterite Viral | C013, C014 |

---

## Estrutura do projeto

```
agente_llm/
├── agent.py              # Loop do agente + tool use (SDK Anthropic)
├── tools.py              # list_symptoms() e search_medical_cases()
├── main.py               # Entrada CLI com conversa multi-turno
├── requirements.txt      # anthropic>=0.112.0
└── RELATORIO_TECNICO.md  # Documentação técnica completa
```

---

## Configurações via variável de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Chave obrigatória |
| `AGENT_MODEL` | `claude-opus-4-8` | Modelo Claude a usar |
| `AGENT_MAX_TOKENS` | `2048` | Limite de tokens na resposta |

Exemplo com modelo alternativo (mais econômico):

```bash
set AGENT_MODEL=claude-haiku-4-5
python main.py
```
