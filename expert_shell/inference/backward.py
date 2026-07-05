"""
Encadeamento para Trás (Backward Chaining).
Parte de uma hipótese-objetivo e tenta prová-la recursivamente,
solicitando ao usuário somente as informações necessárias.
"""
from __future__ import annotations
from typing import Callable, Any
from knowledge_base.kb import KnowledgeBase, Rule


AskUserFn = Callable[[str, list, str], Any]


class BackwardChaining:
    def __init__(
        self,
        kb: KnowledgeBase,
        explainer=None,
        ask_user: AskUserFn | None = None,
    ) -> None:
        self.kb = kb
        self.explainer = explainer
        self.ask_user = ask_user
        self._visited: set[tuple] = set()
        self._skipped: set[str] = set()   # atributos que o usuário pulou (Enter)

    # ── Public ─────────────────────────────────────────────────────────────

    def prove(self, attribute: str, value: Any = None) -> bool:
        """Tenta provar attribute=value. Retorna True se bem-sucedido."""
        self._visited = set()
        # _skipped persiste entre chamadas para não re-perguntar
        return self._prove(attribute, value, parent_rule=None)

    # ── Private ────────────────────────────────────────────────────────────

    def _prove(
        self, attribute: str, value: Any, parent_rule: Rule | None
    ) -> bool:
        # Verifica fatos conhecidos ANTES do controle de ciclos,
        # pois um fato pode ter sido obtido durante a prova de outro objetivo.
        current = self.kb.facts.get(attribute)
        if current is not None:
            return value is None or current == value

        goal_key = (attribute, value)
        if goal_key in self._visited:
            return False
        self._visited.add(goal_key)

        # Encontra regras que concluem este objetivo
        candidate_rules = self.kb.rules_that_conclude(attribute, value)
        if self.explainer:
            self.explainer.record_goal(attribute, value, candidate_rules, parent_rule)

        for rule in candidate_rules:
            if self._try_rule(rule):
                self.kb.add_fact(
                    rule.conclusion.attribute,
                    rule.conclusion.value,
                    inferred=True,
                )
                if self.explainer:
                    self.explainer.record_inference(
                        rule, rule.conclusion.attribute, rule.conclusion.value
                    )
                return True

        # Não pode ser provado por regras → pergunta ao usuário
        if self.ask_user and attribute in self.kb.possible_values:
            if attribute in self._skipped:
                return False   # usuário já pulou esta pergunta antes
            reason = self._build_reason(attribute, parent_rule)
            if self.explainer:
                self.explainer.record_question_reason(attribute, reason)
            user_val = self.ask_user(
                attribute, self.kb.possible_values[attribute], reason
            )
            if user_val is not None:
                self.kb.add_fact(attribute, user_val, inferred=False)
                return value is None or user_val == value
            else:
                self._skipped.add(attribute)

        return False

    def _try_rule(self, rule: Rule) -> bool:
        """Tenta satisfazer todas as condições de uma regra."""
        for condition in rule.conditions:
            if self.explainer:
                self.explainer.record_question_reason(
                    condition.attribute,
                    f"condição da regra {rule.id} ({rule.name}) → "
                    f"{rule.conclusion.attribute} = {rule.conclusion.value}",
                )
            if not self._prove(condition.attribute, condition.value, parent_rule=rule):
                return False
        return True

    def _build_reason(self, attribute: str, parent_rule: Rule | None) -> str:
        if parent_rule:
            return (
                f"condição da regra {parent_rule.id} ({parent_rule.name}), "
                f"que tenta provar '{parent_rule.conclusion.attribute} = "
                f"{parent_rule.conclusion.value}'"
            )
        dependent_rules = self.kb.rules_that_need(attribute)
        if not dependent_rules:
            return f"avaliação de '{attribute}'"
        hyps = {r.conclusion.value for r in dependent_rules}
        return f"avaliação das hipóteses: {', '.join(hyps)}"
