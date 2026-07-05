from cbr_engine import load_cases


def collect_symptoms(symptoms: list) -> dict:
    print("\nInforme os sintomas do paciente.")
    print("Para cada sintoma: [1] Presente  [0] Ausente  [Enter] Pular (ausente)\n")
    query = {}
    for s in symptoms:
        label = s.replace("_", " ").capitalize()
        while True:
            val = input(f"  {label}: ").strip()
            if val in ("", "0", "1"):
                query[s] = int(val) if val != "" else 0
                break
            print("    Use 1, 0 ou Enter para pular.")
    return query


def show_retrieved(retrieved: list) -> None:
    print(f"\n--- Casos similares recuperados (top {len(retrieved)}) ---")
    for i, (sim, case) in enumerate(retrieved, 1):
        print(f"\n  [{i}] Caso {case['id']} — Similaridade: {sim * 100:.1f}%")
        print(f"      Diagnóstico : {case['diagnosis']}")
        present = [s.replace("_", " ") for s, v in case["symptoms"].items() if v == 1]
        print(f"      Sintomas    : {', '.join(present)}")


def show_menu() -> str:
    print("\n=== CBR — Diagnóstico Médico ===")
    print("  [1] Nova consulta")
    print("  [2] Listar casos da base")
    print("  [3] Sair")
    return input("Opção: ").strip()


def list_cases(data: dict) -> None:
    print(f"\nBase contém {len(data['cases'])} casos:\n")
    diseases: dict[str, int] = {}
    for case in data["cases"]:
        d = case["diagnosis"]
        diseases[d] = diseases.get(d, 0) + 1

    for disease, count in sorted(diseases.items()):
        print(f"  {disease}: {count} caso(s)")

    detail = input("\nVer detalhes de um caso? [ID ou Enter para voltar]: ").strip().upper()
    if not detail:
        return
    found = [c for c in data["cases"] if c["id"] == detail]
    if not found:
        print("Caso não encontrado.")
        return
    case = found[0]
    print(f"\nCaso {case['id']} — {case['diagnosis']}")
    print(f"Tratamento: {case['treatment']}")
    present = [s.replace("_", " ") for s, v in case["symptoms"].items() if v == 1]
    print(f"Sintomas presentes: {', '.join(present)}")
