
from libs.input_manager import InputManager
from libs.agent import Agent


def main():
    # Gestisce la terminazione del processo.
    InputManager.handle_interrupt()

    # Setta il nome dell'utente
    InputManager.set_name("luke")

    # Crea un'istanza dell'agente
    agent = Agent(name="Qwen3-4B-Q4_K_M")

    # Ciclo di conversazione
    agent.start_conversation()


# Quando viene eseguito un script Python, il nome del modulo corrente è "__main__"
# quindi, se questo file viene eseguito direttamente, esegui la funzione main().
if __name__ == "__main__":
    main()
