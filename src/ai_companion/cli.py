"""Interfaz de línea de comandos del AI Companion."""

import sys

from .session import CompanionSession

COMPANION_NAME = "Aria"
EXIT_COMMANDS = {"/salir", "/exit", "/quit", "exit", "quit", "salir"}


def run_cli() -> None:
    """Inicia la interfaz interactiva del AI Companion en la terminal."""
    print(f"\n✨ Bienvenido al AI Companion — {COMPANION_NAME} ✨")
    print("─" * 45)

    user_id = input("¿Cuál es tu nombre o ID de usuario? ").strip()
    if not user_id:
        print("Se requiere un nombre o ID para continuar.")
        sys.exit(1)

    session = CompanionSession(user_id=user_id)

    if session.profile.name:
        print(f"\n{COMPANION_NAME}: ¡Hola de nuevo, {session.profile.name}! ¿Cómo estás?")
    else:
        print(f"\n{COMPANION_NAME}: ¡Hola! Soy {COMPANION_NAME}, tu acompañante. ¿Cómo te llamas?")

    print(f"\n(Escribe {'/salir'} para terminar la conversación)\n")

    try:
        while True:
            try:
                user_input = input("Tú: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input:
                continue

            if user_input.lower() in EXIT_COMMANDS:
                print(f"\n{COMPANION_NAME}: ¡Hasta pronto! Fue un placer hablar contigo. 😊")
                break

            response = session.chat(user_input)
            print(f"\n{COMPANION_NAME}: {response}\n")

    finally:
        print("\nGuardando la conversación...")
        session.end_session()
        print("¡Hasta la próxima!")


if __name__ == "__main__":
    run_cli()
