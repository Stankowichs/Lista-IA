"""
Interface de Linha de Comando (CLI) do Expert Shell.
Gerencia o ciclo completo de consulta: coleta de fatos, inferência e explicação.
"""
from __future__ import annotations
import os
import sys

from knowledge_base.kb import KnowledgeBase
from knowledge_base.editor import KBEditor
from inference.forward import ForwardChaining
from inference.backward import BackwardChaining
from inference.hybrid import HybridChaining
from explanation.explainer import Explainer

try:
    from llm.bridge import LLMBridge
    _LLM_IMPORT_OK = True
except ImportError:
    _LLM_IMPORT_OK = False

_SEP  = "-" * 56
_SEP2 = "=" * 56


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


class CLI:
    def __init__(self) -> None:
        self.kb       = KnowledgeBase()
        self.editor   = KBEditor(self.kb)
        self.explainer = Explainer()
        self.llm: LLMBridge | None = None
        self.current_file: str | None = None

    # ── Bootstrap ──────────────────────────────────────────────────────────

    def setup_llm(self) -> None:
        if not _LLM_IMPORT_OK:
            return
        bridge = LLMBridge(self.kb)
        if bridge.is_available():
            self.llm = bridge
        else:
            print("[AVISO] ANTHROPIC_API_KEY não configurada — modo LLM desabilitado.")

    def load_kb_file(self, filepath: str) -> bool:
        try:
            self.kb = KnowledgeBase.load(filepath)
            self.editor = KBEditor(self.kb)
            self.current_file = filepath
            if self.llm:
                self.llm.kb = self.kb
            return True
        except Exception as e:
            print(f"[ERRO] {e}")
            return False

    # ── Main loop ──────────────────────────────────────────────────────────

    def run(self) -> None:
        self.setup_llm()
        self._print_banner()

        while True:
            self._print_main_menu()
            choice = input("Escolha › ").strip()

            if choice == "1":
                self._consultation()
            elif choice == "2":
                self._editor_menu()
            elif choice == "3":
                self._load_dialog()
            elif choice == "4":
                self._save_dialog()
            elif choice == "5":
                print(self.explainer.full_trace())
            elif choice == "6" and self.llm:
                self._nl_consultation()
            elif choice == "7" and self.llm:
                self._llm_suggest_rules()
            elif choice == "0":
                print("\nAté logo!\n")
                break
            else:
                print("Opção inválida.")

    # ── Menus ──────────────────────────────────────────────────────────────

    def _print_banner(self) -> None:
        print(_SEP2)
        print("  EXPERT SHELL — Sistema Especialista em Conhecimento")
        print(_SEP2)
        domain = self.kb.domain_name or "(sem domínio carregado)"
        print(f"  Domínio : {domain}")
        print(f"  Regras  : {len(self.kb.rules)}  |  Hipóteses: {len(self.kb.hypotheses)}")
        print()

    def _print_main_menu(self) -> None:
        print(f"\n{_SEP}")
        print("  MENU PRINCIPAL")
        print(_SEP)
        print("  [1] Nova consulta / diagnóstico")
        print("  [2] Editor da base de conhecimento")
        print("  [3] Carregar base de conhecimento (JSON)")
        print("  [4] Salvar base de conhecimento")
        print("  [5] Ver trilha de inferência da última consulta")
        if self.llm:
            print("  [6] Consulta em linguagem natural (IA)")
            print("  [7] Sugerir novas regras com IA")
        print("  [0] Sair")
        print(_SEP)

    # ── Consultation ───────────────────────────────────────────────────────

    def _consultation(self) -> None:
        if not self.kb.rules:
            print("\n[!] Base vazia. Carregue ou crie regras primeiro.")
            return

        print(f"\n{_SEP2}")
        print("  NOVA CONSULTA")
        print(_SEP2)

        self.kb.reset_session()
        self.explainer.reset()

        print("\nEstratégia de inferência:")
        print("  [1] Encadeamento para Frente  (Forward Chaining)")
        print("  [2] Encadeamento para Trás    (Backward Chaining)")
        print("  [3] Híbrido — recomendado     (Forward + Backward)")
        strategy = input("Estratégia [3] › ").strip() or "3"

        print(f"\n{'─'*40}")
        print("Responda às perguntas. Comandos disponíveis durante a consulta:")
        print("  por que  → explica por que essa pergunta foi feita")
        print("  como     → mostra o raciocínio atual")
        print("  trilha   → exibe a trilha de inferência")
        print(f"{'─'*40}\n")

        if strategy == "1":
            self._run_forward()
        elif strategy == "2":
            self._run_backward()
        else:
            self._run_hybrid()

        self._show_results()

    # strategy runners ──────────────────────────────────────────────────────

    def _run_forward(self) -> None:
        print("[Forward Chaining] Coletando todos os fatos iniciais...\n")
        for attr, values in self.kb.possible_values.items():
            if self.kb.facts.get(attr) is None:
                val = self._ask_user(attr, values, "coleta inicial de fatos")
                if val is not None:
                    self.kb.add_fact(attr, val)
        ForwardChaining(self.kb, self.explainer).run()

    def _run_backward(self) -> None:
        print("[Backward Chaining] Avaliando hipóteses...\n")
        bc = BackwardChaining(self.kb, self.explainer, self._ask_user)
        for hyp in self.kb.hypotheses:
            bc.prove("suspeita", hyp)
            bc.prove("diagnostico", hyp)

    def _run_hybrid(self) -> None:
        print("[Híbrido] Iniciando diagnóstico inteligente...\n")
        HybridChaining(self.kb, self.explainer, self._ask_user).run()

    # ask_user callback ─────────────────────────────────────────────────────

    def _ask_user(
        self, attribute: str, possible_values: list, reason: str
    ) -> str | None:
        label = attribute.replace("_", " ").title()
        opts  = "  |  ".join(str(v) for v in possible_values)
        print(f"[?] {label}")
        print(f"    Valores: {opts}")
        print(f"    (Digite 'por que', 'como', 'trilha' ou Enter para pular)")

        val_lower = {str(v).lower(): v for v in possible_values}

        while True:
            answer = input(f"    Resposta › ").strip().lower()

            if answer == "":
                return None
            if answer in ("por que", "porque"):
                print(f"\n    {self.explainer.why(attribute)}\n")
                continue
            if answer == "como":
                print(f"\n    {self.explainer.how()}\n")
                continue
            if answer == "trilha":
                print(f"\n{self.explainer.full_trace()}\n")
                continue
            if answer in val_lower:
                return val_lower[answer]
            print(f"    Valor inválido. Opções: {opts}")

    # results ───────────────────────────────────────────────────────────────

    def _show_results(self) -> None:
        print(f"\n{_SEP2}")
        print("  RESULTADO DO DIAGNÓSTICO")
        print(_SEP2)

        labels = {
            "diagnostico": "Diagnóstico confirmado",
            "suspeita":    "Suspeita diagnóstica",
            "risco":       "Fator de risco identificado",
        }
        found = False
        for key, label in labels.items():
            val = self.kb.facts.get(key)
            if val:
                found = True
                print(f"\n  {label.upper()}:  {val.upper()}")

        if not found:
            print("\n  Nenhuma conclusão obtida com as informações fornecidas.")
            print("  Tente fornecer mais sintomas ou usar outra estratégia.")

        if self.kb.inferred_facts:
            print(f"\n  Fatos inferidos ({len(self.kb.inferred_facts)}):")
            for attr, val in self.kb.inferred_facts.items():
                print(f"    • {attr} = {val}")

        if self.explainer.inference_trace:
            print(f"\n  Regras disparadas ({len(self.explainer.inference_trace)}):")
            for t in self.explainer.inference_trace:
                r = t["rule"]
                print(f"    • [{r.id}] {r.name}")

        self._post_result_loop()

    def _post_result_loop(self) -> None:
        print(f"\n{_SEP}")
        print("  EXPLICAÇÃO  —  comandos disponíveis:")
        print("  como <atributo>   → como foi determinado o valor")
        print("  por que <attr>    → por que foi perguntado")
        print("  trilha            → trilha completa de inferência")
        if self.llm:
            print("  explicar          → explicação em linguagem natural (IA)")
        print("  voltar            → menu principal")
        print(_SEP)

        while True:
            cmd = input("\n  › ").strip().lower()
            if cmd in ("voltar", "sair", ""):
                break
            elif cmd == "trilha":
                print(self.explainer.full_trace())
            elif cmd.startswith("como "):
                attr = cmd[5:].strip()
                print(f"\n{self.explainer.how(attr)}")
            elif cmd.startswith("por que ") or cmd.startswith("porque "):
                attr = cmd.split(" ", 1)[1].strip()
                print(f"\n{self.explainer.why(attr)}")
            elif cmd == "explicar" and self.llm:
                technical = self.explainer.full_trace()
                print("\n[IA] Gerando explicação natural...")
                print(self.llm.explain_naturally(technical))
            else:
                print("  Comando não reconhecido.")

    # ── Editor ─────────────────────────────────────────────────────────────

    def _editor_menu(self) -> None:
        while True:
            print(f"\n{_SEP}")
            print("  EDITOR DE BASE DE CONHECIMENTO")
            print(_SEP)
            print("  [1]  Listar regras")
            print("  [2]  Ver regra detalhada")
            print("  [3]  Adicionar regra")
            print("  [4]  Remover regra")
            print("  [5]  Listar hipóteses")
            print("  [6]  Adicionar hipótese")
            print("  [7]  Remover hipótese")
            print("  [8]  Listar atributos e valores possíveis")
            print("  [9]  Adicionar atributo com valores")
            print("  [10] Remover atributo")
            print("  [0]  Voltar")
            print(_SEP)
            choice = input("Escolha › ").strip()

            if choice == "1":
                rules = self.editor.list_rules()
                if not rules:
                    print("  Nenhuma regra cadastrada.")
                else:
                    for r in rules:
                        print(f"  {r}")

            elif choice == "2":
                rid = input("  ID da regra › ").strip()
                print(self.editor.show_rule(rid))

            elif choice == "3":
                self._add_rule_dialog()

            elif choice == "4":
                rid = input("  ID da regra a remover › ").strip()
                print(self.editor.remove_rule(rid))

            elif choice == "5":
                hyps = self.kb.hypotheses
                print(f"  Hipóteses ({len(hyps)}): {', '.join(hyps) if hyps else '—'}")

            elif choice == "6":
                hyp = input("  Nova hipótese › ").strip()
                if hyp:
                    print(self.editor.add_hypothesis(hyp))

            elif choice == "7":
                hyp = input("  Hipótese a remover › ").strip()
                print(self.editor.remove_hypothesis(hyp))

            elif choice == "8":
                pv = self.kb.possible_values
                if not pv:
                    print("  Nenhum atributo cadastrado.")
                else:
                    for attr, vals in pv.items():
                        print(f"  • {attr}: {', '.join(str(v) for v in vals)}")

            elif choice == "9":
                attr = input("  Atributo › ").strip()
                raw  = input("  Valores (separados por vírgula) › ").strip()
                if attr and raw:
                    vals = [v.strip() for v in raw.split(",")]
                    print(self.editor.set_possible_values(attr, vals))

            elif choice == "10":
                attr = input("  Atributo a remover › ").strip()
                print(self.editor.remove_attribute(attr))

            elif choice == "0":
                break
            else:
                print("  Opção inválida.")

    def _add_rule_dialog(self) -> None:
        print("\n  [NOVA REGRA]")
        rid  = input("  ID (ex: R30) › ").strip()
        name = input("  Nome › ").strip()
        desc = input("  Descrição (opcional) › ").strip()

        print("  Condições (SE) — Enter vazio para terminar:")
        conditions: list[dict] = []
        while True:
            attr = input("    Atributo › ").strip()
            if not attr:
                break
            val = input(f"    Valor de '{attr}' › ").strip()
            if val:
                conditions.append({"attribute": attr, "value": val})

        if not conditions:
            print("  [!] Regra precisa de pelo menos uma condição.")
            return

        print("  Conclusão (ENTÃO):")
        c_attr = input("    Atributo › ").strip()
        c_val  = input("    Valor › ").strip()

        if c_attr and c_val:
            print(self.editor.add_rule(
                rid, name, conditions,
                {"attribute": c_attr, "value": c_val},
                desc,
            ))
        else:
            print("  [!] Conclusão inválida.")

    # ── Load / Save ────────────────────────────────────────────────────────

    def _load_dialog(self) -> None:
        default = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "domains", "medical.json",
        )
        path = input(f"  Arquivo JSON [{default}] › ").strip() or default
        if self.load_kb_file(path):
            self.explainer.reset()
            print(
                f"  Carregado: {self.kb.domain_name} "
                f"({len(self.kb.rules)} regras, {len(self.kb.hypotheses)} hipóteses)"
            )

    def _save_dialog(self) -> None:
        default = self.current_file or "base.json"
        path = input(f"  Arquivo JSON [{default}] › ").strip() or default
        try:
            self.kb.save(path)
            self.current_file = path
            print(f"  Salvo em: {path}")
        except Exception as e:
            print(f"  [ERRO] {e}")

    # ── LLM features ───────────────────────────────────────────────────────

    def _nl_consultation(self) -> None:
        print("\n[IA] Descreva seus sintomas em linguagem natural:")
        text = input("› ").strip()
        if not text:
            return
        print("[IA] Processando...")
        try:
            facts = self.llm.parse_natural_language(text)
        except Exception as e:
            print(f"[ERRO] {e}")
            return

        if not facts:
            print("[IA] Não foi possível extrair fatos da descrição.")
            return

        print("\nFatos extraídos:")
        for attr, val in facts.items():
            print(f"  • {attr} = {val}")
            self.kb.add_fact(attr, val)

        if input("\nIniciar diagnóstico? (s/n) › ").strip().lower() == "s":
            self.explainer.reset()
            self._run_hybrid()
            self._show_results()

    def _llm_suggest_rules(self) -> None:
        desc = input("[IA] Descreva o tipo de regras que deseja sugerir › ").strip()
        if not desc:
            return
        print("[IA] Gerando sugestões...")
        try:
            suggestions = self.llm.suggest_rules(desc)
        except Exception as e:
            print(f"[ERRO] {e}")
            return

        if not suggestions:
            print("[IA] Nenhuma sugestão gerada.")
            return

        print(f"\n{len(suggestions)} regra(s) sugerida(s):\n")
        for s in suggestions:
            print(f"  {s.get('id')} — {s.get('name')}")
            for c in s.get("conditions", []):
                print(f"    SE {c['attribute']} = {c['value']}")
            conc = s.get("conclusion", {})
            print(f"    ENTÃO {conc.get('attribute')} = {conc.get('value')}")

        if input("\nAdicionar todas à base? (s/n) › ").strip().lower() == "s":
            for s in suggestions:
                result = self.editor.add_rule(
                    s["id"], s["name"],
                    s.get("conditions", []),
                    s.get("conclusion", {}),
                    s.get("description", ""),
                )
                print(f"  {result}")
