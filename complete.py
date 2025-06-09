from libs.input_manager import InputManager
from libs.agent import Agent


def main():
    # Gestisce la terminazione del processo.
    InputManager.handle_interrupt()

    # Setta il nome dell'utente
    InputManager.set_name("luke")

    # Crea un'istanza dell'agente
    agent = Agent(name="Qwen3-4B-Q4_K_M", n_generate=1)

    # Tokenizza una frase
    token = agent.tokenize("Ciao a tutti,")
    print(token)
    
    # De-tokenizza una frase
    testo = agent.detokenize(token)
    print(testo)
    
    # Completa una frase
    frase = "Ciao a tutti,"
    agent.complete_text(frase)


if __name__ == "__main__":
    main()
