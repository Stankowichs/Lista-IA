import sys
from inference import load_knowledge_base, run_session


def main():
    kb = load_knowledge_base()

    print(f"Base carregada: {len(kb['entities'])} animais, {len(kb['attributes'])} atributos.")

    while True:
        run_session(kb)
        again = input("\nJogar novamente? [s/n]: ").strip().lower()
        if again != "s":
            break

    print("Até mais!")


if __name__ == "__main__":
    main()
