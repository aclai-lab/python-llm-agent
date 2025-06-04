import os
from llama_cpp import Llama

from .input_manager import InputManager
from .colors import Colors
from .chat import Chat

MODELS_DIR = "./models/"

class Agent:
    """
    L'agente è un'entità che interagisce con il mondo attraverso il modello LLM.

    Leggi la documentazione completa dei parametri che accetta il costruttore
    del modello LLM per maggiorni informazioni: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/
    """

    def __init__(
            self, name: str,
            n_ctx=2048,
            verbose=False,
            system_prompt: str = "Sei un assistente virtuale che risponde alle domande degli utenti.",
            n_generate: int = 1000,
            think: bool = False):
        """
        Inizializza l'agente.

            Parameters:
                name (str): Il nome del modello LLM da caricare.
        """
        self.name = name

        InputManager.system_message("Caricamento del modello LLM...")

        # Variabile utilitaria per tener traccia del numero di token rimanenti a disposizione per il contesto
        self._remaining_ctx_tokens = None

        # Ricorda se l'agente deve pensare prima di rispondere
        self.think = think

        # Verifica se il modello esiste
        self.model_path = os.path.join(MODELS_DIR, name + ".gguf")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Il modello {self.model_path} non esiste.")

        # Se esiste carica il modello LLM usando llama.cpp via llama-cpp-python
        InputManager.system_message("Messaggi del modello: ", new_line=False)
        self.llm = Llama(model_path=self.model_path, n_ctx=n_ctx, verbose=verbose)
        self.chat = Chat(self.llm, n_generate=n_generate, system_prompt=system_prompt, think=think)
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
        self._prompt = prompt + " /no_think" if not self.think else prompt
        self.chat.send_message(self.chat.USER_KEY, prompt)

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
        self._response, self._remaining_ctx_tokens = self.chat.generate_assistant_reply()
        self._clean_response()

    def respond_incremental(self):
        """
        Mostra la risposta del modello LLM in modo incrementale.
        """
        print(f"{self.get_name()}: ", end="")
        yield self.chat.generate_assistant_reply_stepped()

    def start_conversation(self, incremental=False):
        InputManager.system_message("Puoi iniziare a conversare con l'LLM!")
        InputManager.system_message("Scrivi 'esci' per terminare.")
        InputManager.system_message("Scrivi 'stats' per vedere le statistiche.")
        InputManager.system_message("Scrivi 'clear' per cancellare il contesto.")

        try:
            while True:
                # Mostra il prompt e attendi l'input dell'utente
                InputManager.prompt()
                self.say(input())

                # Se l'utente ha scritto "esci" o "exit" o "quit" allora termina la conversazione
                if InputManager.is_exit_word(self.raw_user_prompt()):
                    InputManager.system_message("Conversazione terminata.")
                    break

                if InputManager.is_clear_context_word(self.raw_user_prompt()):
                    self.reset_chat()
                    continue

                if InputManager.is_stats_word(self.raw_user_prompt()):
                    self.show_stats()
                    continue

                if incremental:
                    # Mostra la risposta dell'LLM in modo incrementale
                    for response in self.respond_incremental():
                        print(response, end="", flush=True)
                else:
                    # Mostra l'intera risposta dell'LLM direttamente quando è completamente generata
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

    def _clean_response(self):
        """
        Pulisce la risposta dell'LLM rimuovendo i caratteri speciali.
        """
        self._response = '\n'.join([l.strip() for l in self._response.splitlines() if l.strip() and "think>" not in l])

    def reset_chat(self):
        """
        Resetta la conversazione.
        """
        self.chat.reset_chat(keep_system=True)
        self.respond("Conversazione resettata: non ricordo più nulla :(")

    def raw_user_prompt(self):
        """
        Restituisce il prompt dell'utente.
        """
        return self._prompt.replace("/no_think", "").strip()

    def show_stats(self):
        """
        Mostra le statistiche sull'utilizzo del modello LLM.
        """
        InputManager.system_message(f"  token usati: {self.chat.tokens_used()}")
        InputManager.system_message(f"  token rimanenti: {self.chat.context_available()}")