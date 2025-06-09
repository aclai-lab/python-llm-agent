import os
import sys
import ctypes
from llama_cpp import Llama, llama_log_set

from .input_manager import InputManager
from .colors import Colors
from .chat import Chat

MODELS_DIR = "./models/"

class Agent:
    """
    Classe Agent che gestisce l'interazione con un modello LLM tramite llama.cpp.

    Questa classe fornisce un'interfaccia per caricare un modello LLM, gestire le conversazioni
    e fornire risposte incrementali o complete agli utenti.
    """

    def __init__(self,
        name: str,
        n_ctx=2048,
        verbose=False,
        system_prompt: str = "Sei un assistente virtuale che risponde alle domande degli utenti.",
        n_generate: int = 1024
    ):
        """
        Inizializza un nuovo agente LLM.

        @param name: Nome del modello da caricare (senza estensione .gguf)
        @param n_ctx: Dimensione del contesto in token (default: 2048)
        @param verbose: Se True, mostra output dettagliato durante il caricamento (default: False)
        @param system_prompt: Prompt di sistema per inizializzare il comportamento dell'AI (default: messaggio in italiano)
        @param n_generate: Numero massimo di token da generare per risposta (default: 1024)
        """
        if not verbose:
            def my_log_callback(level, message, user_data): pass
            log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)(my_log_callback)
            llama_log_set(log_callback, ctypes.c_void_p())

        self.name = name
        self._prompt = ''
        InputManager.system_message("Caricamento del modello LLM...")

        # Verifica se il modello esiste
        self.model_path = os.path.join(MODELS_DIR, name + ".gguf")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Il modello {self.model_path} non esiste.")

        # Se esiste carica il modello LLM usando llama.cpp via llama-cpp-python
        self.llm = Llama(model_path=self.model_path, n_ctx=n_ctx, verbose=verbose, seed=42)
        self.chat = Chat(self.llm, n_generate=n_generate)
        self.chat.send_message(Chat.SYSTEM_KEY, system_prompt)
        InputManager.system_message("Modello caricato.")

        # Il modello saluta l'utente
        self._show_llm_response("Ciao, sono un'intelligenza artificiale che può rispondere a qualsiasi domanda.")
        self._show_llm_response("Qual è la tua domanda?")

    def _get_name(self):
        """
        Restituisce il nome dell'agente formattato con colori.

        @return: Nome dell'agente colorato in ciano
        """
        return Colors.cyan(self.name)

    def _send_prompt_to_llm(self, prompt: str):
        """
        Invia un prompt al modello LLM.

        @param prompt: Il testo del prompt da inviare al modello
        """
        self.chat.send_message(self.chat.USER_KEY, prompt)
        self._prompt = prompt

    def _show_llm_response(self, response=None):
        """
        Mostra la risposta dell'LLM nella console.

        @param response: La risposta da mostrare. Se None, usa self._response (default: None)
        """
        if response is not None:
            self._response = response
        print(f"{self._get_name()}: {self._response.strip()}")

    def _generate_llm_response(self):
        """
        Genera una risposta completa dall'LLM e la memorizza in self._response.

        Questo metodo genera l'intera risposta prima di restituirla.
        """
        self._response, self._remaining_ctx_tokens = self.chat.generate_assistant_reply()

    def _generate_llm_response_incremental(self):
        """
        Genera una risposta dall'LLM in modo incrementale (token per token).

        Questo metodo filtra automaticamente i tag <think></think> vuoti per fornire
        una migliore esperienza utente durante la generazione incrementale.

        @return: Generator che produce token di risposta uno alla volta
        """
        print(f"{self._get_name()}: ", end="")
        
        in_think_check = False
        think_is_empty = False
        
        for token in self.chat.generate_assistant_reply_stepped():
            if not in_think_check:
                if token == "<think>" or token == "</think>":
                    in_think_check = True
                    think_is_empty = True
                else:
                    yield token
            else:
                if token == "</think>":
                    in_think_check = False
                    if not think_is_empty: yield token
                    continue
                
                if len(token.strip()) != 0:
                    if think_is_empty:
                        think_is_empty = False
                        yield "<think>\n"
                    yield token

    def start_conversation(self, incremental=True, forget=False):
        """
        Avvia una conversazione interattiva con l'LLM.

        Questo metodo gestisce il loop principale della conversazione, permettendo all'utente
        di interagire con il modello attraverso comandi speciali e input di testo.

        Comandi supportati:
        - 'esci', 'exit', 'quit': Termina la conversazione
        - 'clear': Cancella il contesto della conversazione
        - 'stats': Mostra statistiche sui token utilizzati

        @param incremental: Se True, mostra le risposte token per token; se False, mostra la risposta completa (default: True)
        """
        InputManager.system_message("Puoi iniziare a conversare con l'LLM!")
        InputManager.system_message("Scrivi 'esci' per terminare.")
        InputManager.system_message("Scrivi 'stats' per vedere le statistiche.")
        InputManager.system_message("Scrivi 'clear' per cancellare il contesto.")

        try:
            while True:
                # Mostra il prompt e attendi l'input dell'utente
                InputManager.show_user_prompt()

                # Use multiline input support
                user_input = InputManager._get_multiline_input()

                # Se l'utente ha scritto "esci" o "exit" o "quit" allora termina la conversazione
                if InputManager.is_exit_word(user_input):
                    InputManager.system_message("Conversazione terminata.")
                    break

                if InputManager.is_clear_context_word(user_input):
                    self._reset_chat()
                    continue

                if InputManager.is_stats_word(user_input):
                    self._show_stats()
                    continue
                
                if '/think' not in user_input:
                    user_input += ' /no_think'
                self._send_prompt_to_llm(user_input)

                if incremental:
                    # Mostra la risposta dell'LLM in modo incrementale
                    for response in self._generate_llm_response_incremental():
                        print(response, end="", flush=True)
                else:
                    # Mostra l'intera risposta dell'LLM direttamente quando è completamente generata
                    # Invia il prompt all'LLM e ricevi la risposta
                    self._generate_llm_response()

                    # Mostra la risposta dell'LLM
                    self._show_llm_response()
                if forget:
                    self._reset_chat(silent=True)
        except KeyboardInterrupt:
            print()
            InputManager.system_message("Conversazione terminata.")
        except Exception as e:
            if isinstance(e, EOFError):
                print()
                InputManager.system_message("Conversazione terminata.")
            else:
                InputManager.error(f"Si è verificato un errore: {e}")

    def send_instruction(self, incremental=True):
        """
        Invia un'istruzione all'LLM.
        """
        self.start_conversation(incremental=incremental, forget=True)

    def _reset_chat(self, silent=False):
        """
        Resetta il contesto della conversazione mantenendo il prompt di sistema.

        Questo metodo cancella tutta la cronologia della conversazione ma mantiene
        il prompt di sistema originale per preservare il comportamento dell'AI.
        """
        self.chat.reset_chat(keep_system=True)
        if not silent:
            self._show_llm_response("Conversazione resettata: non ricordo più nulla :(")

    def _show_stats(self):
        """
        Mostra le statistiche sui token utilizzati e disponibili.

        Visualizza informazioni utili per monitorare l'utilizzo del contesto:
        - Token utilizzati nella conversazione corrente
        - Token rimanenti nel contesto disponibile
        """
        InputManager.system_message(f"  token usati: {self.chat.tokens_used()}")
        InputManager.system_message(f"  token rimanenti: {self.chat.context_available()}")
