# Expert Shell — Sistema Especialista Baseado em Conhecimento

**Disciplina:** Inteligência Artificial — 2026.1  
**Professor:** Evandro Costa  
**Aluno:** Renato Coca Terrazas Freire  

---

## Descrição do Projeto

Foi implementada uma **shell genérica** para construção de aplicações baseadas em conhecimento, nos moldes do Expert-SINTA. A ferramenta permite que especialistas de qualquer domínio criem e executem sistemas de diagnóstico/recomendação apenas definindo uma base de conhecimento em JSON, sem alterar o código-fonte.

Como aplicação demonstrativa, foi construída uma **base de diagnóstico médico** com 28 regras, 36 atributos e 11 hipóteses de diagnóstico.

---

## Pré-requisitos

- Python 3.10 ou superior
- Sem dependências externas obrigatórias (tudo da biblioteca padrão)
- *(Opcional)* Pacote `anthropic` para o módulo de IA generativa: `pip install anthropic`

---

## Como Rodar

### 1. Abrir o terminal na pasta do projeto

### 2. Configurar encoding UTF-8 (necessário no Windows)

**PowerShell:**
```powershell
$env:PYTHONIOENCODING = "utf-8"
```

**CMD:**
```cmd
set PYTHONIOENCODING=utf-8
```

### 3. Executar

```bash
python main.py
```

A base de diagnóstico médico é carregada automaticamente.

### 4. *(Opcional)* Ativar integração com IA Generativa

```powershell
$env:ANTHROPIC_API_KEY = "sua-chave-aqui"
python main.py
```

---

## Como Usar o Sistema

Ao iniciar, o menu principal é exibido:

```
[1] Nova consulta / diagnóstico
[2] Editor da base de conhecimento
[3] Carregar base de conhecimento (JSON)
[4] Salvar base de conhecimento
[5] Ver trilha de inferência da última consulta
[0] Sair
```

### Realizando uma consulta

1. Escolha `[1] Nova consulta`
2. Escolha a estratégia de inferência (pressione Enter para usar o **Híbrido**, recomendado)
3. Responda as perguntas digitando exatamente um dos valores entre parênteses
4. Pressione **Enter** sem digitar nada para pular uma pergunta
5. O diagnóstico e as regras ativadas são exibidos ao final

### Comandos disponíveis durante a consulta

| Comando | Efeito |
|---|---|
| `por que` | Explica por que aquela pergunta foi feita |
| `como` | Mostra o raciocínio até o momento |
| `trilha` | Exibe toda a cadeia de inferência |

### Cenários de teste prontos

| Diagnóstico esperado | Respostas |
|---|---|
| Gripe | febre=`alta`, tosse=`seca`, dor_muscular=`sim`, fadiga=`sim` |
| COVID-19 | perda_olfato=`sim`, perda_paladar=`sim` |
| Dengue | exposicao_aedes=`sim`, febre=`alta`, enjoo=`sim`, dor_cabeca=`sim` |
| Pneumonia | tosse=`produtiva`, falta_ar_repouso=`sim`, febre=`alta`, exame_rx_torace=`infiltrado` |
| Diabetes Tipo 2 | glicemia=`alta`, sede_excessiva=`sim`, frequencia_urinaria=`alta` |
| Hipertensão | pressao_arterial=`alta`, historico_hipertensao=`sim` |

---

## Arquitetura Implementada

```
expert_shell/
├── knowledge_base/
│   ├── kb.py         # Fatos, regras, base de conhecimento e persistência JSON
│   └── editor.py     # CRUD de fatos, regras, hipóteses e atributos
├── inference/
│   ├── forward.py    # Encadeamento para frente
│   ├── backward.py   # Encadeamento para trás
│   └── hybrid.py     # Estratégia híbrida
├── explanation/
│   └── explainer.py  # Mecanismo de explicação (Por quê? / Como?)
├── llm/
│   └── bridge.py     # Integração com Claude API (IA Generativa)
├── interface/
│   └── cli.py        # Interface de linha de comando
├── domains/
│   └── medical.json  # Base demonstrativa de diagnóstico médico
└── main.py           # Ponto de entrada
```

---

## Módulos Implementados

### 1. Base de Conhecimento (`kb.py`, `editor.py`)

A base de conhecimento é composta por três elementos principais:

- **Fatos:** pares `atributo = valor` que representam o estado atual do mundo (ex: `febre = alta`)
- **Regras de produção:** estrutura `SE condição1 E condição2 ... ENTÃO conclusão`
- **Hipóteses:** lista de diagnósticos possíveis que o motor tentará provar ou refutar

A persistência é feita em **JSON**, permitindo que especialistas criem e editem bases sem tocar no código. Exemplo de regra:

```json
{
  "id": "R01",
  "name": "Gripe Clássica",
  "conditions": [
    {"attribute": "febre",        "value": "alta"},
    {"attribute": "tosse",        "value": "seca"},
    {"attribute": "dor_muscular", "value": "sim"},
    {"attribute": "fadiga",       "value": "sim"}
  ],
  "conclusion": {"attribute": "suspeita", "value": "gripe"}
}
```

O editor (`editor.py`) expõe operações CRUD completas: adicionar, remover e listar fatos, regras e hipóteses, além de gerenciar os valores válidos de cada atributo.

### 2. Motor de Inferência

Foram implementadas três estratégias:

#### Encadeamento para Frente (`forward.py`)

Parte dos fatos conhecidos e dispara regras repetidamente até que não haja mais inferências possíveis. Cada regra é disparada no máximo uma vez por sessão. Útil quando o usuário já fornece todos os dados iniciais.

#### Encadeamento para Trás (`backward.py`)

Parte de uma hipótese-objetivo (ex: `suspeita = gripe`) e tenta prová-la recursivamente. Para cada condição não satisfeita, tenta encontrar uma regra que a prove ou, se não houver, pergunta ao usuário. Assim, só são feitas perguntas relevantes para as hipóteses em avaliação.

Dois cuidados de implementação foram necessários:
- A verificação dos fatos já conhecidos precisa ocorrer **antes** do controle de ciclos, para que fatos obtidos durante a prova de uma hipótese sejam reaproveitados em outras
- Atributos que o usuário pular (Enter em branco) são registrados em um conjunto `_skipped` para não serem perguntados novamente

#### Estratégia Híbrida (`hybrid.py`)

Combina as duas abordagens:
1. Executa o encadeamento para frente com os fatos iniciais
2. Para cada hipótese, executa o encadeamento para trás (coletando apenas o necessário)
3. Após cada resposta do usuário, propaga imediatamente via encadeamento para frente

É a estratégia padrão recomendada por ser mais eficiente e interativa.

### 3. Mecanismo de Explicação (`explainer.py`)

Registra toda a trilha de raciocínio durante a inferência e responde a duas perguntas:

- **Por quê?** — justifica por que uma pergunta foi feita, indicando qual regra e qual hipótese dependem daquela informação
- **Como?** — explica como uma conclusão foi obtida, listando as regras disparadas e as condições que as satisfizeram

Exemplo de saída do `por que`:

```
Perguntei sobre 'exposicao_aedes' porque é condição da regra R09
(Dengue com Exposição ao Aedes), que tenta provar 'suspeita = dengue'.
```

Exemplo de saída do `como`:

```
Regra R09 — Dengue com Exposição ao Aedes
  Condições satisfeitas: exposicao_aedes = sim E febre = alta E enjoo = sim E dor_cabeca = sim
  Conclusão gerada:      suspeita = dengue
```

### 4. Interface com o Usuário (`cli.py`)

Interface de linha de comando com menus interativos para:
- Realizar consultas de diagnóstico com qualquer das três estratégias
- Editar a base de conhecimento em tempo de execução
- Carregar e salvar bases em JSON
- Consultar a trilha de inferência e as explicações

### 5. Integração com IA Generativa (`bridge.py`) — Bônus

Integração com a API da Anthropic (Claude) para três funcionalidades adicionais:
- **Entrada em linguagem natural:** o usuário descreve os sintomas em texto livre e o LLM extrai os fatos estruturados correspondentes
- **Explicação enriquecida:** converte a explicação técnica do motor de inferência em linguagem natural acessível ao paciente
- **Sugestão de regras:** dado um texto descrevendo o domínio, o LLM propõe novas regras de produção no formato esperado pela shell

O processo de inferência continua sendo realizado integralmente pelo motor baseado em regras; o LLM atua apenas como auxiliar de linguagem.

---

## Base Demonstrativa — Diagnóstico Médico

### Estatísticas

| Item | Quantidade |
|---|---|
| Regras de produção | 28 |
| Atributos (fatos possíveis) | 36 |
| Hipóteses de diagnóstico | 11 |

### Diagnósticos cobertos

| Diagnóstico | Regras principais |
|---|---|
| Gripe | R01, R02 |
| COVID-19 | R03, R04, R05 |
| Dengue | R08, R09, R10 |
| Dengue Hemorrágica | R11 |
| Pneumonia | R13, R14, R15 |
| Diabetes Tipo 2 | R16, R17 |
| Hipertensão Arterial | R19, R20 |
| Alergia Respiratória | R21, R22 |
| Gastroenterite | R23, R24 |
| Infecção Urinária | R25, R26 |
| Anemia | R27 |

Além dos diagnósticos, o sistema identifica fatores de risco (`risco = covid_grave`, `risco = dengue_grave`, etc.) via regras encadeadas sobre diagnósticos já estabelecidos.

### Atributos coletados

```
febre, tosse, coriza, dor_garganta, dor_muscular, fadiga,
perda_olfato, perda_paladar, dificuldade_respirar, falta_ar_repouso,
dor_cabeca, dor_retro_orbital, manchas_pele, sangramentos, plaquetas,
exposicao_aedes, glicemia, sede_excessiva, frequencia_urinaria,
visao_turva, historico_diabetes, imc, pressao_arterial,
historico_hipertensao, espirros, olhos_vermelhos, diarreia, vomito,
enjoo, dor_abdominal, ardencia_urinar, palidez, idade,
vacinado_covid, exame_rx_torace, crepitacao_pulmao
```

---

## Extensibilidade

A shell é genérica — qualquer domínio pode ser adicionado criando um novo arquivo JSON em `domains/` seguindo a mesma estrutura do `medical.json`. O código-fonte não precisa ser alterado.

Para carregar outro domínio:
```bash
python main.py domains/outro_dominio.json
```

Ou via menu `[3] Carregar base de conhecimento` durante a execução.

---

## Exemplos de Consultas Realizadas

As saídas abaixo foram geradas pelo próprio sistema, usando a estratégia híbrida.

### Consulta 1 — Gripe

O paciente relata febre alta, tosse seca, dor muscular e fadiga. O sistema perguntou apenas os atributos necessários para avaliar as hipóteses e chegou ao diagnóstico em uma única regra.

```
  [?] febre (alta/moderada/baixa/ausente) > alta
  [?] tosse (seca/produtiva/ausente) > seca
  [?] dor_muscular (sim/nao) > sim
  [?] fadiga (sim/nao) > sim

--- RESULTADO ---
  Suspeita: GRIPE

--- REGRAS DISPARADAS ---
  [R01] Gripe Clássica
       SE febre = alta E tosse = seca E dor_muscular = sim E fadiga = sim
       ENTAO suspeita = gripe
```

**Resposta ao "Por quê?" para `dor_muscular`:**
```
Perguntei sobre 'dor_muscular' porque é condição da regra R01 (Gripe Clássica),
que tenta provar 'suspeita = gripe'.
Essa informação permite ao motor de inferência decidir quais regras podem ser disparadas.
```

**Resposta ao "Como?" para `suspeita = gripe`:**
```
Regra R01 — Gripe Clássica
  Condições satisfeitas: febre = alta E tosse = seca E dor_muscular = sim E fadiga = sim
  Conclusão gerada:      suspeita = gripe
```

---

### Consulta 2 — Dengue

O paciente relata exposição ao mosquito Aedes, febre alta, enjoo, dor de cabeça e manchas na pele com sangramentos. O sistema chegou à suspeita de dengue pela regra R09 e identificou encadeamento para dengue hemorrágica via R11.

```
  [?] febre (alta/moderada/baixa/ausente) > alta
  [?] tosse (seca/produtiva/ausente) > (pulado)
  [?] perda_olfato (sim/nao) > (pulado)
  [?] dor_retro_orbital (sim/nao) > (pulado)
  [?] exposicao_aedes (sim/nao) > sim
  [?] enjoo (sim/nao) > sim
  [?] dor_cabeca (sim/nao) > sim

--- RESULTADO ---
  Suspeita: DENGUE
```

**Trilha completa de inferência:**
```
+== TRILHA DE INFERENCIA ==+

Passo 1: [R09] Dengue com Exposição ao Aedes
  SE   exposicao_aedes = sim E febre = alta E enjoo = sim E dor_cabeca = sim
  ENTAO suspeita = dengue

+==========================+
```

Nota: atributos marcados como `(pulado)` foram descartados pelo mecanismo de `_skipped` do encadeamento para trás — o sistema não os reperguntou nas hipóteses seguintes.

---

### Consulta 3 — Pneumonia confirmada por RX

Este cenário demonstra o **encadeamento em cadeia**: a regra R13 infere `suspeita = pneumonia` a partir dos sintomas; o encadeamento para frente então verifica se R15 pode disparar, o que exige o resultado do RX de tórax. Quando o usuário fornece `infiltrado`, a conclusão sobe para `diagnostico = pneumonia`.

```
  [?] febre (alta/moderada/baixa/ausente) > alta
  [?] tosse (seca/produtiva/ausente) > produtiva
  [?] perda_olfato (sim/nao) > (pulado)
  [?] dor_retro_orbital (sim/nao) > (pulado)
  [?] exposicao_aedes (sim/nao) > (pulado)
  [?] falta_ar_repouso (sim/nao) > sim
  [?] exame_rx_torace (infiltrado/normal) > infiltrado

--- RESULTADO ---
  Suspeita:    PNEUMONIA
  Diagnostico: PNEUMONIA

--- REGRAS DISPARADAS ---
  [R13] Pneumonia Bacteriana
       SE tosse = produtiva E falta_ar_repouso = sim E febre = alta
       ENTAO suspeita = pneumonia

  [R15] Pneumonia Confirmada por RX
       SE suspeita = pneumonia E exame_rx_torace = infiltrado
       ENTAO diagnostico = pneumonia
```

**Resposta ao "Como?" para `diagnostico = pneumonia`:**
```
Regra R15 — Pneumonia Confirmada por RX
  Condições satisfeitas: suspeita = pneumonia E exame_rx_torace = infiltrado
  Conclusão gerada:      diagnostico = pneumonia
```

---

## Limitações e Possíveis Melhorias

### Limitações

**1. Valores exatos e sem tolerância a sinônimos**
O motor de inferência compara atributo-valor por igualdade exata (`febre = alta`). O usuário precisa digitar exatamente o valor listado. Não há tratamento de sinônimos, abreviações ou erros de digitação.

**2. Sem graus de certeza**
O sistema trabalha com lógica booleana pura: uma regra dispara ou não dispara. Não há mecanismo de fatores de certeza (como no MYCIN) nem probabilidades (como em Redes Bayesianas). Sintomas ambíguos ou parcialmente presentes não são tratados.

**3. Conclusão única por atributo**
A base de conhecimento armazena apenas um valor por atributo. Se duas regras concluírem `suspeita = gripe` e `suspeita = covid19`, a segunda sobrescreve a primeira. O sistema não mantém uma lista de diagnósticos simultâneos com pesos.

**4. Perguntas dependentes do ordenamento das regras**
O encadeamento para trás percorre as hipóteses na ordem em que aparecem no JSON. Dependendo da ordem, o sistema pode fazer perguntas sobre uma hipótese improvável antes de perguntas sobre a mais provável.

**5. Base de conhecimento estática durante a consulta**
Não é possível adicionar regras ou fatos durante uma sessão de consulta ativa. O editor só é acessível pelo menu principal.

**6. Interface exclusivamente textual**
A interface é de linha de comando. Não há interface gráfica nem aplicação web, o que limita a usabilidade para usuários finais não técnicos.

---

### Possíveis Melhorias

**1. Fatores de certeza (modelo MYCIN)**
Associar um grau de confiança (0 a 1) a cada regra e a cada fato fornecido pelo usuário, propagando a incerteza ao longo da inferência. Isso permitiria lidar com sintomas parciais e retornar diagnósticos com percentual de confiança.

**2. Múltiplos diagnósticos ranqueados**
Em vez de sobrescrever o valor de `suspeita`, manter uma lista ordenada de hipóteses com seus respectivos pesos acumulados, apresentando ao final os diagnósticos mais prováveis em ordem decrescente.

**3. Seleção inteligente de perguntas**
Implementar uma heurística para escolher qual atributo perguntar a seguir com base no ganho de informação esperado — priorizando perguntas que discriminam mais hipóteses ao mesmo tempo, similar ao funcionamento do Akinator.

**4. Interface gráfica ou web**
Desenvolver uma interface Flask/FastAPI com formulário interativo, tornando o sistema acessível pelo navegador sem necessidade de terminal.

**5. Persistência de sessão e histórico**
Salvar o histórico de consultas em banco de dados, permitindo auditoria dos diagnósticos realizados e aprendizado incremental da base de conhecimento a partir de casos reais.

**6. Integração mais profunda com LLM**
Atualmente o LLM é usado apenas para parsing de linguagem natural e geração de explicações. Uma melhoria seria usar o LLM para sugerir quais perguntas fazer com base no contexto da conversa, tornando a interação mais natural e menos sequencial.

---

> **Observação:** O sistema tem finalidade exclusivamente educacional e não deve ser utilizado como ferramenta real de diagnóstico médico.
