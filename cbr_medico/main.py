from cbr_engine import load_cases, retrieve, reuse, revise, retain
from interface import collect_symptoms, show_retrieved, show_menu, list_cases


def run_consultation(data: dict) -> None:
    query = collect_symptoms(data["symptoms"])

    present = [s for s, v in query.items() if v == 1]
    if not present:
        print("Nenhum sintoma informado. Consulta cancelada.")
        return

    print(f"\nSintomas informados: {', '.join(s.replace('_', ' ') for s in present)}")

    retrieved = retrieve(query, data, top_k=3)
    show_retrieved(retrieved)

    proposal = reuse(retrieved)
    if not proposal:
        print("Nenhum caso similar encontrado na base.")
        return

    revised = revise(proposal)
    retain(query, revised, data)


def main():
    data = load_cases()
    print(f"\nSistema CBR — Diagnóstico Médico")
    print(f"Base: {len(data['cases'])} casos, {len(data['symptoms'])} sintomas")

    while True:
        choice = show_menu()
        if choice == "1":
            run_consultation(data)
            data = load_cases()
        elif choice == "2":
            list_cases(data)
        elif choice == "3":
            print("Encerrando.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
