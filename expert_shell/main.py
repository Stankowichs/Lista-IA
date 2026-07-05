#!/usr/bin/env python3
"""
Expert Shell — ponto de entrada principal.

Uso:
  python main.py                      # carrega medical.json automaticamente
  python main.py domains/outro.json   # carrega outro domínio
"""
import sys
import os

# Garante UTF-8 no terminal Windows (evita erros com acentos)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Garante que os submódulos sejam encontrados independente de onde o script é chamado
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interface.cli import CLI


def main() -> None:
    cli = CLI()

    domain_file: str
    if len(sys.argv) > 1:
        domain_file = sys.argv[1]
    else:
        domain_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "domains", "medical.json",
        )

    if os.path.exists(domain_file):
        ok = cli.load_kb_file(domain_file)
        if ok:
            kb = cli.kb
            print(
                f"[OK] Domínio carregado: {kb.domain_name}\n"
                f"     {len(kb.rules)} regras  |  "
                f"{len(kb.hypotheses)} hipóteses  |  "
                f"{len(kb.possible_values)} atributos\n"
            )
        else:
            print(f"[AVISO] Não foi possível carregar: {domain_file}\n")
    else:
        print(f"[AVISO] Arquivo não encontrado: {domain_file}")
        print("        Inicie sem base carregada ou use o editor para criar uma.\n")

    cli.run()


if __name__ == "__main__":
    main()
