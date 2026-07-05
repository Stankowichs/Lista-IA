# Expert Shell — Sistema Especialista Baseado em Conhecimento

Sistema especialista genérico (shell) desenvolvido em Python para a disciplina de **Inteligência Artificial (2026.1)** da UFAL, professor Evandro Costa.

Permite que especialistas de qualquer domínio construam aplicações de diagnóstico e recomendação apenas definindo uma base de conhecimento em JSON — sem alterar o código-fonte.

---

## Funcionalidades

- **Editor de base de conhecimento** — cadastro e manutenção de fatos, regras SE...ENTÃO, hipóteses e atributos
- **Motor de inferência** com três estratégias:
  - Encadeamento para Frente (Forward Chaining)
  - Encadeamento para Trás (Backward Chaining)
  - Estratégia Híbrida (recomendada)
- **Mecanismo de explicação** — responde *Por quê?* e *Como?* durante e após a consulta
- **Persistência em JSON** — bases de conhecimento salvas e carregadas em arquivo
- **Integração com IA Generativa** — entrada em linguagem natural via Claude API (opcional)
- **Base demonstrativa** de diagnóstico médico com 28 regras, 36 atributos e 11 diagnósticos

---

## Como Rodar

**Pré-requisito:** Python 3.10+

```bash
cd expert_shell

# Windows — configurar encoding
$env:PYTHONIOENCODING = "utf-8"   # PowerShell
# set PYTHONIOENCODING=utf-8      # CMD

python main.py
```

A base de diagnóstico médico é carregada automaticamente.

### Ativar integração com IA (opcional)

```bash
pip install anthropic
$env:ANTHROPIC_API_KEY = "sua-chave-aqui"
python main.py
```

---

## Cenários de Teste

| Diagnóstico | Respostas durante a consulta |
|---|---|
| Gripe | febre=`alta`, tosse=`seca`, dor_muscular=`sim`, fadiga=`sim` |
| COVID-19 | perda_olfato=`sim`, perda_paladar=`sim` |
| Dengue | exposicao_aedes=`sim`, febre=`alta`, enjoo=`sim`, dor_cabeca=`sim` |
| Pneumonia | tosse=`produtiva`, falta_ar_repouso=`sim`, febre=`alta`, exame_rx_torace=`infiltrado` |
| Diabetes | glicemia=`alta`, sede_excessiva=`sim`, frequencia_urinaria=`alta` |

Durante a consulta, a qualquer momento digite:
- `por que` → explica por que aquela pergunta foi feita
- `como` → mostra o raciocínio atual
- `trilha` → exibe toda a cadeia de inferência

---

## Estrutura do Projeto

```
expert_shell/
├── knowledge_base/
│   ├── kb.py         # Fatos, regras e persistência JSON
│   └── editor.py     # CRUD da base de conhecimento
├── inference/
│   ├── forward.py    # Encadeamento para frente
│   ├── backward.py   # Encadeamento para trás
│   └── hybrid.py     # Estratégia híbrida
├── explanation/
│   └── explainer.py  # Mecanismo de explicação (Por quê? / Como?)
├── llm/
│   └── bridge.py     # Integração com Claude API
├── interface/
│   └── cli.py        # Interface de linha de comando
├── domains/
│   └── medical.json  # Base demonstrativa de diagnóstico médico
└── main.py
```

Para documentação técnica completa, consulte [RELATORIO_TECNICO.md](RELATORIO_TECNICO.md).

---

> Sistema desenvolvido para fins educacionais. Não deve ser utilizado como ferramenta real de diagnóstico médico.
