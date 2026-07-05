# Relatório Técnico — Questão 3: Agente Baseado em LLM

**Disciplina:** Inteligência Artificial — AB2 2026.1  
**Professor:** Evandro Costa — UFAL  
**Aluno:** Renato Coca  
**Questão:** 3 — Aplicação envolvendo agentes baseados em LLM (2 pontos)

---

## 1. Descrição da Aplicação

O sistema implementado é um **Agente de Triagem Médica** que combina dois paradigmas de IA:

- **LLM (Large Language Model):** Claude Opus 4.8 (Anthropic) atua como agente central — compreende linguagem natural, raciocina sobre sintomas e explica diagnósticos.
- **CBR (Case-Based Reasoning):** o mesmo motor de raciocínio baseado em casos da Questão 2.4 é reutilizado como *ferramenta* chamada pelo agente.

O usuário descreve seus sintomas em linguagem natural (português). O agente consulta a base de casos via *tool use*, interpreta os resultados e fornece um diagnóstico provável com tratamento sugerido — tudo em linguagem natural e de forma empática.

> **Aviso:** a aplicação tem finalidade exclusivamente educacional e não substitui diagnóstico médico profissional.

---

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    main.py (CLI)                    │
│  Loop de conversa multi-turno c/ histórico completo │
└───────────────────┬─────────────────────────────────┘
                    │ mensagem do usuário
                    ▼
┌─────────────────────────────────────────────────────┐
│              agent.py  —  run_agent_turn()          │
│                                                     │
│  1. POST /v1/messages  →  Claude Opus 4.8           │
│     (tools=[list_symptoms, search_medical_cases])   │
│                                                     │
│  2. stop_reason == "tool_use"?                      │
│     Sim → executa ferramenta local → appenda        │
│            tool_result → volta ao passo 1           │
│     Não → retorna texto final ao usuário            │
└───────────────────┬─────────────────────────────────┘
                    │ chamadas de ferramentas
                    ▼
┌─────────────────────────────────────────────────────┐
│               tools.py  —  Tool Functions           │
│                                                     │
│  list_symptoms()          → 20 sintomas rastreados  │
│  search_medical_cases()   → top-3 por cosseno       │
│                              (reutiliza cbr_engine) │
└───────────────────┬─────────────────────────────────┘
                    │ importa
                    ▼
┌─────────────────────────────────────────────────────┐
│   ../cbr_medico/cbr_engine.py  (Questão 2.4)        │
│   ../cbr_medico/cases.json     (17 casos, 7 doenças)│
└─────────────────────────────────────────────────────┘
```

### Arquivos do projeto

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Entrada CLI; loop de conversa; validação da API key |
| `agent.py` | Loop do agente; chama SDK Anthropic; executa ferramentas |
| `tools.py` | Implementações das ferramentas; ponte para o CBR |
| `requirements.txt` | Dependência: `anthropic>=0.112.0` |

---

## 3. Conceito de Agente Baseado em LLM

Um **agente baseado em LLM** é um sistema onde o modelo de linguagem não apenas gera texto, mas **decide quais ações executar** para cumprir um objetivo. O ciclo é:

```
Percepção (mensagem do usuário)
        ↓
   Raciocínio (LLM delibera)
        ↓
   Ação (chama ferramenta)
        ↓
  Observação (resultado da ferramenta)
        ↓
[repete até conclusão]
        ↓
   Resposta final ao usuário
```

Nesta implementação:
- **Percepção:** descrição de sintomas em linguagem natural
- **Ferramentas (ações):** `list_symptoms` e `search_medical_cases`
- **Memória:** histórico de conversa passado a cada chamada da API (multi-turno stateful)
- **Raciocínio:** Claude usa `thinking: adaptive` — pensa sobre quais ferramentas chamar e em que ordem, e depois sintetiza os resultados em linguagem natural

---

## 4. Tool Use (Chamada de Ferramentas)

O SDK Anthropic implementa *tool use* via o protocolo de mensagens. Cada ferramenta é descrita com JSON Schema:

```python
{
    "name": "search_medical_cases",
    "description": "Busca na base CBR usando similaridade de cosseno...",
    "input_schema": {
        "type": "object",
        "properties": {
            "symptoms": {
                "type": "object",
                "additionalProperties": {"type": "integer", "enum": [0, 1]}
            }
        },
        "required": ["symptoms"]
    }
}
```

Quando Claude decide chamar uma ferramenta, a resposta tem `stop_reason == "tool_use"` e um bloco `ToolUseBlock` no conteúdo. O código executa localmente a função Python correspondente e devolve o resultado como `tool_result` — o modelo então recebe o resultado e continua o raciocínio.

### Ferramentas implementadas

#### `list_symptoms()`
Retorna a lista dos 20 sintomas rastreados no banco de casos. Claude chama esta ferramenta primeiro para conhecer o vocabulário exato antes de construir o vetor de sintomas.

#### `search_medical_cases(symptoms: dict)`
Constrói o vetor binário de consulta e delega para `retrieve()` do motor CBR:

```python
query = {s: int(symptoms.get(s, 0)) for s in symptom_list}
retrieved = retrieve(query, data, top_k=3)
```

A similaridade de cosseno é calculada sobre os 20 sintomas binários. Os 3 casos mais similares retornam com `similarity_pct`, `diagnosis` e `treatment`.

---

## 5. Integração com o CBR (Questão 2.4)

O módulo `cbr_engine.py` é importado diretamente:

```python
CBR_PATH = Path(__file__).parent.parent / "cbr_medico"
sys.path.insert(0, str(CBR_PATH))
from cbr_engine import load_cases, retrieve
```

Isso elimina duplicação de código e demonstra **composição de sistemas de IA**: o agente LLM orquestra o sistema baseado em conhecimento (CBR) como uma ferramenta especializada.

A base de casos possui 17 casos e 7 diagnósticos: Gripe (Influenza), COVID-19, Dengue, Pneumonia Bacteriana, Malária, Resfriado Comum e Gastroenterite Viral.

---

## 6. Modelo Utilizado

**Claude Opus 4.8** (`claude-opus-4-8`) — modelo padrão da plataforma Anthropic.

Parâmetros:
- `max_tokens`: 2048
- `thinking`: `{"type": "adaptive"}` — Claude usa raciocínio interno extendido quando necessário
- `tools`: lista das 2 ferramentas descritas acima
- Histórico completo de conversa passado a cada turno (memória multi-turno)

O modelo pode ser substituído via variável de ambiente `AGENT_MODEL`:
```bash
set AGENT_MODEL=claude-haiku-4-5  # alternativa mais econômica
```

---

## 7. Exemplo de Interação

```
Você: Estou com febre alta, perda do olfato e dificuldade para respirar.

  [ferramenta: list_symptoms]
  [ferramenta: search_medical_cases]

Agente: Com base nos sintomas relatados — febre, perda de olfato e
        dificuldade respiratória — o sistema identificou alta similaridade
        (87,3%) com casos de COVID-19.

        Diagnóstico mais provável: COVID-19
        Tratamento sugerido: Isolamento 10 dias, monitorar saturação
        de O₂, antitérmicos; suporte médico se SpO₂ < 94%.

        Casos diferenciais (similaridade menor):
        • Gripe (Influenza) — 62,1%
        • Pneumonia Bacteriana — 58,4%

        ⚠️ IMPORTANTE: Este é um sistema educacional. Procure um médico
        para avaliação e diagnóstico definitivo.
```

---

## 8. Como Executar

### Pré-requisitos
```bash
pip install anthropic>=0.112.0
```

### Configurar API Key
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Linux / macOS
export ANTHROPIC_API_KEY=sk-ant-...
```

### Executar
```bash
cd C:\Programs\IA\agente_llm
python main.py
```

### Usar modelo alternativo (opcional)
```bash
set AGENT_MODEL=claude-haiku-4-5
python main.py
```

---

## 9. Referências

- Anthropic SDK Python: https://github.com/anthropics/anthropic-sdk-python  
- Tool use documentation: https://docs.anthropic.com/en/docs/tool-use  
- CBR — Questão 2.4 deste trabalho: `../cbr_medico/`
