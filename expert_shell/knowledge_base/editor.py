"""
Editor da Base de Conhecimento.
Operações CRUD para fatos, regras, hipóteses e valores possíveis.
"""
from __future__ import annotations
from .kb import KnowledgeBase, Rule, Condition


class KBEditor:
    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    # ── Facts ──────────────────────────────────────────────────────────────

    def add_fact(self, attribute: str, value) -> str:
        self.kb.add_fact(attribute, value)
        return f"Fato adicionado: {attribute} = {value}"

    def remove_fact(self, attribute: str) -> str:
        if self.kb.remove_fact(attribute):
            return f"Fato removido: {attribute}"
        return f"Fato não encontrado: {attribute}"

    def list_facts(self) -> list[tuple]:
        return list(self.kb.facts.items())

    # ── Rules ──────────────────────────────────────────────────────────────

    def add_rule(
        self,
        rule_id: str,
        name: str,
        conditions: list[dict],
        conclusion: dict,
        description: str = "",
    ) -> str:
        try:
            rule = Rule(
                id=rule_id,
                name=name,
                conditions=[Condition(**c) for c in conditions],
                conclusion=Condition(**conclusion),
                description=description,
            )
            self.kb.add_rule(rule)
            return f"Regra '{rule_id}' adicionada com sucesso."
        except ValueError as e:
            return f"Erro: {e}"

    def remove_rule(self, rule_id: str) -> str:
        if self.kb.remove_rule(rule_id):
            return f"Regra '{rule_id}' removida."
        return f"Regra '{rule_id}' não encontrada."

    def update_rule(self, rule_id: str, new_rule: Rule) -> str:
        if self.kb.update_rule(rule_id, new_rule):
            return f"Regra '{rule_id}' atualizada."
        return f"Regra '{rule_id}' não encontrada."

    def list_rules(self) -> list[Rule]:
        return self.kb.rules

    def show_rule(self, rule_id: str) -> str:
        rule = self.kb.get_rule(rule_id)
        if not rule:
            return f"Regra '{rule_id}' não encontrada."
        lines = [
            f"ID:          {rule.id}",
            f"Nome:        {rule.name}",
            f"Descrição:   {rule.description}",
            "Condições:   SE",
        ]
        for c in rule.conditions:
            lines.append(f"               {c}")
        lines.append(f"Conclusão:   ENTÃO {rule.conclusion}")
        return "\n".join(lines)

    # ── Hypotheses ─────────────────────────────────────────────────────────

    def add_hypothesis(self, hypothesis: str) -> str:
        if hypothesis in self.kb.hypotheses:
            return f"Hipótese '{hypothesis}' já existe."
        self.kb.hypotheses.append(hypothesis)
        return f"Hipótese '{hypothesis}' adicionada."

    def remove_hypothesis(self, hypothesis: str) -> str:
        if hypothesis not in self.kb.hypotheses:
            return f"Hipótese '{hypothesis}' não encontrada."
        self.kb.hypotheses.remove(hypothesis)
        return f"Hipótese '{hypothesis}' removida."

    # ── Possible Values ────────────────────────────────────────────────────

    def set_possible_values(self, attribute: str, values: list) -> str:
        self.kb.possible_values[attribute] = values
        return f"Valores para '{attribute}': {values}"

    def remove_attribute(self, attribute: str) -> str:
        if attribute in self.kb.possible_values:
            del self.kb.possible_values[attribute]
            return f"Atributo '{attribute}' removido."
        return f"Atributo '{attribute}' não encontrado."
