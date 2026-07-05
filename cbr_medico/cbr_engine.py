import json
from pathlib import Path


CASES_PATH = Path(__file__).parent / "cases.json"


def load_cases() -> dict:
    with open(CASES_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_cases(data: dict) -> None:
    with open(CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cosine_similarity(a: dict, b: dict, symptoms: list) -> float:
    dot = sum(a.get(s, 0) * b.get(s, 0) for s in symptoms)
    norm_a = sum(a.get(s, 0) ** 2 for s in symptoms) ** 0.5
    norm_b = sum(b.get(s, 0) ** 2 for s in symptoms) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve(query_symptoms: dict, data: dict, top_k: int = 3) -> list:
    symptoms = data["symptoms"]
    scored = []
    for case in data["cases"]:
        sim = cosine_similarity(query_symptoms, case["symptoms"], symptoms)
        scored.append((sim, case))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def reuse(retrieved: list) -> dict:
    if not retrieved:
        return {}
    best_sim, best_case = retrieved[0]
    return {
        "diagnosis": best_case["diagnosis"],
        "treatment": best_case["treatment"],
        "confidence": round(best_sim * 100, 1),
        "source_case": best_case["id"],
    }


def revise(proposal: dict) -> dict:
    print(f"\n--- Diagnóstico sugerido ---")
    print(f"  Diagnóstico : {proposal['diagnosis']}")
    print(f"  Tratamento  : {proposal['treatment']}")
    print(f"  Confiança   : {proposal['confidence']}%")
    print(f"  Caso base   : {proposal['source_case']}")

    confirm = input("\nO diagnóstico está correto? [s/n]: ").strip().lower()
    if confirm == "s":
        proposal["validated"] = True
        return proposal

    new_diag = input("Informe o diagnóstico correto: ").strip()
    new_treat = input("Informe o tratamento correto: ").strip()
    proposal["diagnosis"] = new_diag
    proposal["treatment"] = new_treat
    proposal["validated"] = True
    return proposal


def retain(query_symptoms: dict, proposal: dict, data: dict) -> None:
    save_choice = input("\nDeseja salvar este caso na base? [s/n]: ").strip().lower()
    if save_choice != "s":
        print("Caso não armazenado.")
        return

    existing_ids = [c["id"] for c in data["cases"]]
    numeric = [int(i[1:]) for i in existing_ids if i.startswith("C") and i[1:].isdigit()]
    new_id = f"C{max(numeric) + 1:03d}" if numeric else "C001"

    new_case = {
        "id": new_id,
        "symptoms": query_symptoms,
        "diagnosis": proposal["diagnosis"],
        "treatment": proposal["treatment"],
        "validated": proposal.get("validated", True),
    }
    data["cases"].append(new_case)
    save_cases(data)
    print(f"Caso {new_id} armazenado com sucesso.")
