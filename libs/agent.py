import os
from llama_cpp import Llama

from .input_manager import InputManager
from .colors import Colors

MODELS_DIR = "./models/"

class Agent:
    """
    L'agente è un'entità che interagisce con il mondo attraverso il modello LLM.

    Leggi la documentazione completa dei parametri che accetta il costruttore
    del modello LLM per maggiorni informazioni: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/
    """

    def __init__(self, name: str, n_ctx=2048, verbose=False):
        """
        Inizializza l'agente.

            Parameters:
                name (str): Il nome del modello LLM da caricare.
        """
        self.name = name

        InputManager.system_message("Caricamento del modello LLM...")

        # Verifica se il modello esiste
        self.model_path = os.path.join(MODELS_DIR, name + ".gguf")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Il modello {self.model_path} non esiste.")

        # Se esiste carica il modello LLM usando llama.cpp via llama-cpp-python
        InputManager.system_message("Messaggi del modello: ", new_line=False)
        self.llm = Llama(model_path=self.model_path, n_ctx=n_ctx, verbose=verbose)
        InputManager.system_message("Modello caricato.")

        # Il modello saluta l'utente
        self.respond("Ciao, sono un'intelligenza artificiale che può rispondere a qualsiasi domanda.")
        self.respond("Qual è la tua domanda?")

    def get_name(self):
        """
        Restituisce il nome (colorato) dell'agente.
        """
        return Colors.cyan(self.name)

    def say(self, prompt: str):
        """
        Invia un prompt all'LLM e riceve la risposta.
        """
        self._prompt = prompt

    def respond(self, response=None):
        """
        Mostra la risposta del modello LLM.
        """
        if response is not None:
            self._response = response
        print(f"{self.get_name()}: {self._response.strip()}")

    def _process_prompt(self):
        """
        Manda il prompt all'LLM e riceve la risposta.
        """
        self._response = self.llm(self._prompt)["choices"][0]["text"]

    def start_conversation(self):
        InputManager.system_message("Puoi iniziare a conversare con l'LLM!")
        InputManager.system_message("Scrivi 'esci' per terminare.")

        try:
            while True:
                # Mostra il prompt e attendi l'input dell'utente
                InputManager.prompt()
                self.say(input())

                # Se l'utente ha scritto "esci" o "exit" o "quit" allora termina la conversazione
                if InputManager._is_exit_word(self._prompt):
                    InputManager.system_message("Conversazione terminata.")
                    break

                # Invia il prompt all'LLM e ricevi la risposta
                self._process_prompt()

                # Mostra la risposta dell'LLM
                self.respond()
        except KeyboardInterrupt:
            print()
            InputManager.system_message("Conversazione terminata.")
        except Exception as e:
            if isinstance(e, EOFError):
                print()
                InputManager.system_message("Conversazione terminata.")
            else:
                InputManager.error(f"Si è verificato un errore: {e}")
