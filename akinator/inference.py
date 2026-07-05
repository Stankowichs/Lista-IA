import json
from pathlib import Path


def load_knowledge_base(path: str = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "knowledge_base.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def select_best_attribute(candidates: list, asked: set, kb: dict) -> dict | None:
    best_attr = None
    best_score = -1

    for attr in kb["attributes"]:
        if attr["id"] in asked:
            continue

        yes_count = sum(
            1 for e in candidates
            if e["attributes"].get(attr["id"]) is True
        )
        no_count = len(candidates) - yes_count
        score = min(yes_count, no_count)

        if score > best_score:
            best_score = score
            best_attr = attr

    return best_attr


def filter_candidates(candidates: list, attr_id: str, answer: str) -> list:
    if answer == "s":
        return [e for e in candidates if e["attributes"].get(attr_id) is True]
    elif answer == "n":
        return [e for e in candidates if e["attributes"].get(attr_id) is False]
    return candidates


def run_session(kb: dict) -> None:
    candidates = list(kb["entities"])
    asked = set()
    question_count = 0

    print("\n=== AKINATOR — Adivinhe o Animal ===")
    print("Pense em um animal. Responderei Sim (s), Não (n) ou Não sei (ns).\n")

    while len(candidates) > 1:
        attr = select_best_attribute(candidates, asked, kb)

        if attr is None:
            break

        print(f"Pergunta {question_count + 1}: {attr['question']}")
        while True:
            resp = input("  [s] Sim  [n] Não  [ns] Não sei: ").strip().lower()
            if resp in ("s", "n", "ns"):
                break
            print("  Resposta inválida. Use s, n ou ns.")

        asked.add(attr["id"])
        question_count += 1
        candidates = filter_candidates(candidates, attr["id"], resp)

        if len(candidates) == 0:
            print("\nNão consigo identificar o animal. Desisti!")
            return

        if len(candidates) == 1:
            break

        print(f"  (Hipóteses restantes: {len(candidates)})\n")

    if len(candidates) == 1:
        print(f"\nMinha resposta: **{candidates[0]['name']}**!")
        confirm = input("Acertei? [s/n]: ").strip().lower()
        if confirm == "s":
            print(f"Excelente! Acertei em {question_count} pergunta(s).")
        else:
            print("Errei dessa vez. Qual era o animal?")
            name = input("Nome do animal: ").strip()
            print(f"Obrigado! Anotei '{name}' para aprender mais.")
    elif len(candidates) > 1:
        top = candidates[0]["name"]
        print(f"\nFiquei em dúvida, mas meu melhor palpite é: **{top}**")
        print(f"Candidatos restantes: {', '.join(e['name'] for e in candidates)}")
    else:
        print("\nFicaram sem candidatos. Não consigo adivinhar!")
