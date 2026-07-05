import os
import sys
from agent import run_agent_turn, MODEL

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          AGENTE DE TRIAGEM MÉDICA  —  LLM + CBR              ║
║  Modelo : {model:<49}║
║  Disciplina : IA — AB2 2026.1 — Prof. Evandro Costa — UFAL  ║
╚══════════════════════════════════════════════════════════════╝
  AVISO: ferramenta EXCLUSIVAMENTE EDUCACIONAL.
         Não substitui diagnóstico médico profissional.

  Digite 'sair' para encerrar.
"""


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Erro: variável ANTHROPIC_API_KEY não definida.")
        print("Execute: set ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    print(BANNER.format(model=MODEL))
    conversation: list = []

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando. Cuide-se!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print("Encerrando. Cuide-se!")
            break

        conversation.append({"role": "user", "content": user_input})

        print("\nAgente: ", end="", flush=True)
        reply = run_agent_turn(conversation)
        print(reply)
        print()


if __name__ == "__main__":
    main()
