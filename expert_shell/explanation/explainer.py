"""
Mecanismo de Explicação.
Responde 'Por quê?' e 'Como?' para o usuário,
mantendo uma trilha completa do raciocínio.
"""
from __future__ import annotations
from knowledge_base.kb import Rule


class Explainer:
    def __init__(self) -> None:
        self.inference_trace: list[dict] = []
        self.goal_trace: list[dict] = []
        self.question_reasons: dict[str, str] = {}

    # ── Recording ──────────────────────────────────────────────────────────

    def record_inference(self, rule: Rule, attribute: str, value) -> None:
        self.inference_trace.append(
            {"rule": rule, "attribute": attribute, "value": value}
        )

    def record_goal(
        self,
        attribute: str,
        value,
        candidate_rules: list[Rule],
        parent_rule: Rule | None,
    ) -> None:
        self.goal_trace.append(
            {
                "attribute": attribute,
                "value": value,
                "candidate_rules": candidate_rules,
                "parent_rule": parent_rule,
            }
        )

    def record_question_reason(self, attribute: str, reason: str) -> None:
        # Registra apenas a razão mais específica (a primeira que aparecer)
        if attribute not in self.question_reasons:
            self.question_reasons[attribute] = reason

    # ── Explanations ───────────────────────────────────────────────────────

    def why(self, attribute: str) -> str:
        """Por que foi perguntado sobre *attribute*?"""
        reason = self.question_reasons.get(attribute)
        if reason:
            return (
                f"Perguntei sobre '{attribute}' porque é {reason}.\n"
                f"Essa informação permite ao motor de inferência decidir\n"
                f"quais regras podem ser disparadas."
            )

        # Tenta reconstruir pelo goal_trace
        relevant = [g for g in self.goal_trace if g["attribute"] == attribute]
        if relevant:
            g = relevant[-1]
            parent = g.get("parent_rule")
            if parent:
                return (
                    f"Perguntei sobre '{attribute}' porque é uma condição\n"
                    f"da regra {parent.id} ({parent.name}),\n"
                    f"que tenta concluir: {parent.conclusion}."
                )
            rules = g["candidate_rules"]
            if rules:
                hyps = {r.conclusion.value for r in rules}
                ids = ", ".join(r.id for r in rules)
                return (
                    f"Perguntei sobre '{attribute}' porque estou avaliando\n"
                    f"as hipóteses: {', '.join(hyps)}.\n"
                    f"Regras envolvidas: {ids}."
                )

        return (
            f"'{attribute}' é uma informação relevante para o diagnóstico,\n"
            f"mas não encontrei um contexto específico registrado."
        )

    def how(self, attribute: str | None = None, value=None) -> str:
        """Como foi concluído *attribute* = *value*?"""
        trace = self.inference_trace
        if attribute:
            trace = [t for t in trace if t["attribute"] == attribute]
        if value is not None and attribute:
            trace = [t for t in trace if t["value"] == value]

        if not trace:
            target = f"'{attribute} = {value}'" if attribute else "qualquer conclusão"
            return f"Nenhuma inferência registrada para {target}."

        lines = []
        for entry in trace:
            rule: Rule = entry["rule"]
            conds = " E ".join(str(c) for c in rule.conditions)
            lines.append(
                f"Regra {rule.id} — {rule.name}\n"
                f"  Condições satisfeitas: {conds}\n"
                f"  Conclusão gerada:      {entry['attribute']} = {entry['value']}"
            )
        return "\n\n".join(lines)

    def full_trace(self) -> str:
        """Trilha completa de inferência em ordem cronológica."""
        if not self.inference_trace:
            return "Nenhuma inferência realizada nesta sessão."
        lines = ["+== TRILHA DE INFERENCIA ==+"]
        for i, entry in enumerate(self.inference_trace, 1):
            rule: Rule = entry["rule"]
            conds = " E ".join(str(c) for c in rule.conditions)
            lines.append(
                f"\nPasso {i}: [{rule.id}] {rule.name}\n"
                f"  SE   {conds}\n"
                f"  ENTAO {entry['attribute']} = {entry['value']}"
            )
        lines.append("\n+==========================+")
        return "\n".join(lines)

    def reset(self) -> None:
        self.inference_trace.clear()
        self.goal_trace.clear()
        self.question_reasons.clear()
