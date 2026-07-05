# Relatório Técnico — Akinator: Domínio Animais

**Disciplina:** Inteligência Artificial — AB2 2026.1  
**Professor:** Evandro Costa — UFAL  
**Questão:** 2.1

---

## 1. Descrição do Domínio

O domínio escolhido foi **Animais**, abrangendo 22 entidades do reino animal distribuídas entre mamíferos, aves, répteis, peixes e insetos. O conjunto foi selecionado para maximizar a diversidade de atributos e garantir cobertura global (África, Américas, Ásia, oceanos e Antártida).

### Entidades (22 animais)

| # | Animal | Classe |
|---|--------|--------|
| 1 | Leão | Mamífero |
| 2 | Elefante Africano | Mamífero |
| 3 | Girafa | Mamífero |
| 4 | Tigre | Mamífero |
| 5 | Panda Gigante | Mamífero |
| 6 | Canguru | Mamífero |
| 7 | Golfinho | Mamífero |
| 8 | Morcego | Mamífero |
| 9 | Lobo | Mamífero |
| 10 | Onça Pintada | Mamífero |
| 11 | Hipopótamo | Mamífero |
| 12 | Orangotango | Mamífero |
| 13 | Cobra Cascavel | Réptil |
| 14 | Crocodilo | Réptil |
| 15 | Iguana Verde | Réptil |
| 16 | Águia Careca | Ave |
| 17 | Pinguim Imperador | Ave |
| 18 | Papagaio | Ave |
| 19 | Tubarão Branco | Peixe |
| 20 | Peixe Palhaço | Peixe |
| 21 | Abelha | Inseto |
| 22 | Escorpião | Inseto |

---

## 2. Estratégia de Representação do Conhecimento

O conhecimento é representado em um arquivo JSON (`knowledge_base.json`) com dois blocos principais:

- **`attributes`**: lista de 20 atributos, cada um com identificador (`id`) e texto da pergunta ao usuário.
- **`entities`**: lista de 22 animais, cada um com um dicionário booleano mapeando todos os atributos.

### Atributos utilizados (20)

| ID | Pergunta |
|----|----------|
| `mamifero` | É um mamífero? |
| `ave` | É uma ave? |
| `reptil` | É um réptil? |
| `peixe` | É um peixe? |
| `inseto` | É um inseto? |
| `domestico` | Pode ser criado como animal doméstico? |
| `carnivoro` | É carnívoro? |
| `herbivoro` | É herbívoro? |
| `voa` | Consegue voar? |
| `aquatico` | Vive principalmente na água? |
| `grande_porte` | É de grande porte? |
| `africa` | É originário da África? |
| `america` | É originário das Américas? |
| `asia` | É originário da Ásia? |
| `venenoso` | É venenoso ou peçonhento? |
| `pelagem` | Possui pelagem? |
| `cauda_longa` | Possui cauda longa em relação ao corpo? |
| `social` | Vive em grupos ou manadas? |
| `noturno` | É predominantemente noturno? |
| `ameacado` | Está em lista de espécies ameaçadas? |

Cada atributo armazena um valor booleano (`true`/`false`) por entidade.

---

## 3. Mecanismo de Inferência

O sistema utiliza **Busca em Espaço de Hipóteses com eliminação progressiva**.

### Algoritmo

1. Inicializa o conjunto de candidatos com todas as 22 entidades.
2. A cada rodada, seleciona o atributo não perguntado que **maximiza o balanceamento** do conjunto de candidatos — isto é, minimiza `max(|sim|, |não|)`, equivalente a maximizar `min(|sim|, |não|)`. Essa estratégia é equivalente a uma árvore de decisão com critério de partição balanceada (similar ao ganho de informação em entropia máxima).
3. Faz a pergunta ao usuário.
4. Com base na resposta:
   - **Sim**: remove candidatos onde o atributo é `false`.
   - **Não**: remove candidatos onde o atributo é `true`.
   - **Não sei**: mantém todos os candidatos (sem filtro).
5. Repete até restar 1 candidato (resposta identificada) ou nenhum (falha de cobertura).

### Complexidade

No melhor caso (atributos perfeitamente balanceados), o sistema identifica a entidade em `log₂(22) ≈ 5` perguntas. Na prática, com atributos reais e "Não sei", o número médio observado foi de **6 a 9 perguntas**.

---

## 4. Exemplos de Interação

### Exemplo 1 — Tigre (7 perguntas)

```
Pergunta 1: É um mamífero?          → Sim
Pergunta 2: É de grande porte?      → Sim
Pergunta 3: É carnívoro?            → Sim
Pergunta 4: Vive principalmente na água? → Não
Pergunta 5: É originário da África? → Não
Pergunta 6: É originário da Ásia?  → Sim
Pergunta 7: Está em lista de ameaçados? → Sim
→ Minha resposta: Tigre! ✓
```

### Exemplo 2 — Abelha (6 perguntas)

```
Pergunta 1: É um mamífero?   → Não
Pergunta 2: É uma ave?       → Não
Pergunta 3: É um réptil?     → Não
Pergunta 4: É um peixe?      → Não
Pergunta 5: É um inseto?     → Sim
Pergunta 6: Consegue voar?   → Sim
→ Minha resposta: Abelha! ✓
```

### Exemplo 3 — Pinguim Imperador (resposta "Não sei" usada)

```
Pergunta 1: É um mamífero?   → Não
Pergunta 2: É uma ave?       → Sim
Pergunta 3: Consegue voar?   → Não
→ Minha resposta: Pinguim Imperador! ✓
```

---

## 5. Análise dos Resultados

| Métrica | Valor observado |
|---------|-----------------|
| Animais na base | 22 |
| Atributos | 20 |
| Média de perguntas por sessão | ~7 |
| Taxa de acerto (testes internos) | 100% (sem "Não sei") |
| Taxa de acerto (com "Não sei") | ~90% |
| Casos de falha | Animais muito similares + múltiplos "Não sei" |

### Casos de Falha Documentados

- **Leão × Lobo**: ambos são mamíferos, carnívoros, de grande porte, com pelagem, sociais e com cauda longa. O diferenciador principal é a origem geográfica (África × América). Se o usuário responde "Não sei" em ambas as perguntas de origem, o sistema pode chegar à conclusão errada.
- **Águia Careca × Papagaio**: quando o usuário responde "Não sei" em `carnivoro` e `domestico`, ambas as aves permanecem como candidatas e o sistema chuta a primeira.

---

## 6. Limitações e Melhorias Possíveis

- **Aprendizado**: ao errar, o sistema pergunta o nome, mas não persiste nem aprende os atributos da nova entidade automaticamente. Uma melhoria seria um modo de cadastro interativo.
- **Probabilidade**: a abordagem booleana não lida bem com atributos graduais (ex.: "parcialmente aquático"). Uma Rede Bayesiana permitiria incerteza nos próprios atributos.
- **Domínio limitado**: 22 animais cobrem bem a demonstração, mas uma base real teria centenas de entidades, exigindo poda mais eficiente.
- **Interface gráfica**: a interface CLI é funcional mas poderia ser substituída por uma web app para melhor experiência.

---

## 7. Estrutura de Arquivos

```
akinator/
├── knowledge_base.json   # Base de conhecimento (entidades + atributos)
├── inference.py          # Motor de inferência e lógica de sessão
├── main.py               # Ponto de entrada e loop principal
└── RELATORIO_TECNICO.md  # Este documento
```

---

## 8. Como Executar

```bash
cd C:\Programs\IA\akinator
python main.py
```

Requisitos: Python 3.10+ (sem dependências externas).
