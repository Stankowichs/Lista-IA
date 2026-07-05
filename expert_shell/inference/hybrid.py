"""
Estratégia Híbrida de Inferência.
Combina encadeamento para frente e para trás:
  1. FC com os fatos iniciais (expansão rápida)
  2. BC por hipótese (coleta apenas o necessário)
  3. Novo FC após cada resposta do usuário (propagação imediata)
"""
from __future__ import annotations
from typing import Callable, Any
from knowledge_base.kb import KnowledgeBase
from .forward import ForwardChaining
from .backward import BackwardChaining


class HybridChaining:
    def __init__(
        self,
        kb: KnowledgeBase,
        explainer=None,
        ask_user: Callable | None = None,
    ) -> None:
        self.kb = kb
        self.explainer = explainer
        self.forward = ForwardChaining(kb, explainer)
        self.backward = BackwardChaining(kb, explainer, self._wrapped_ask(ask_user))

    # ── Public ─────────────────────────────────────────────────────────────

    def run(self, hypotheses: list[str] | None = None) -> dict[str, bool]:
        """
        Executa a estratégia híbrida para cada hipótese.
        Retorna {hipótese: True/False}.
        """
        if hypotheses is None:
            hypotheses = self.kb.hypotheses

        # Fase 1: FC com fatos já conhecidos
        self.forward.run()

        results: dict[str, bool] = {}
        for hyp in hypotheses:
            # Avalia as duas formas de conclusão independentemente
            # (não usar `or` para evitar short-circuit)
            proved_s = self.backward.prove("suspeita", hyp)
            proved_d = self.backward.prove("diagnostico", hyp)
            results[hyp] = proved_s or proved_d
            # Fase 3: propaga inferências após cada rodada de BC
            self.forward.run()

        # FC final para capturar cadeias geradas pelas inferências
        self.forward.run()
        return results

    def conclusions(self) -> dict[str, str]:
        """Retorna os fatos de conclusão (suspeita / diagnostico / risco)."""
        out = {}
        for key in ("suspeita", "diagnostico", "risco"):
            val = self.kb.facts.get(key)
            if val:
                out[key] = val
        return out

    # ── Private ────────────────────────────────────────────────────────────

    def _wrapped_ask(self, ask_user: Callable | None) -> Callable | None:
        """Envolve o ask_user para rodar FC imediatamente após cada resposta."""
        if ask_user is None:
            return None

        def wrapper(attribute: str, possible_values: list, reason: str) -> Any:
            val = ask_user(attribute, possible_values, reason)
            if val is not None:
                # Propaga imediatamente o novo fato
                self.forward.run()
            return val

        return wrapper
