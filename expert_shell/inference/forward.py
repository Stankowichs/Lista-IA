"""
Encadeamento para Frente (Forward Chaining).
Parte dos fatos conhecidos e dispara regras até não haver mais inferências.
"""
from __future__ import annotations
from knowledge_base.kb import KnowledgeBase, Rule


class ForwardChaining:
    def __init__(self, kb: KnowledgeBase, explainer=None) -> None:
        self.kb = kb
        self.explainer = explainer

    def run(self) -> dict[str, object]:
        """
        Executa o loop de inferência.
        Retorna todos os novos fatos inferidos nesta rodada.
        """
        inferred: dict = {}
        fired_ids: set[str] = set()
        changed = True

        while changed:
            changed = False
            for rule in self.kb.rules:
                if rule.id in fired_ids:
                    continue
                if rule.can_fire(self.kb.facts):
                    attr = rule.conclusion.attribute
                    val = rule.conclusion.value
                    if self.kb.facts.get(attr) != val:
                        self.kb.add_fact(attr, val, inferred=True)
                        inferred[attr] = val
                        fired_ids.add(rule.id)
                        changed = True
                        if self.explainer:
                            self.explainer.record_inference(rule, attr, val)

        return inferred

    def applicable_rules(self) -> list[Rule]:
        """Regras que podem disparar com os fatos atuais."""
        return [r for r in self.kb.rules if r.can_fire(self.kb.facts)]
