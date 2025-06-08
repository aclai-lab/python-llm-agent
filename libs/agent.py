import os
import sys
import select
import ctypes
from llama_cpp import Llama, llama_log_set

from .input_manager import InputManager
from .colors import Colors
from .chat import Chat

MODELS_DIR = "./models/"

class Agent:

    def __init__(self,
        name: str,
        n_ctx=2048,
        verbose=False,
        system_prompt: str = "Sei un assistente virtuale che risponde alle domande degli utenti.",
        n_generate: int = 1024
    ):
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
        self.llm = Llama(model_path=self.model_path, n_ctx=n_ctx, verbose=verbose)
        self.chat = Chat(self.llm, n_generate=n_generate)
        InputManager.system_message("Modello caricato.")

        # Il modello saluta l'utente
        self._show_llm_response("Ciao, sono un'intelligenza artificiale che può rispondere a qualsiasi domanda.")
        self._show_llm_response("Qual è la tua domanda?")

    def _get_name(self):
        return Colors.cyan(self.name)

    def _send_prompt_to_llm(self, prompt: str):
        self.chat.send_message(self.chat.USER_KEY, prompt)
        self._prompt = prompt

    def _show_llm_response(self, response=None):
        if response is not None:
            self._response = response
        print(f"{self._get_name()}: {self._response.strip()}")

    def _generate_llm_response(self):
        self._response, self._remaining_ctx_tokens = self.chat.generate_assistant_reply()

    def _generate_llm_response_incremental(self):
        print(f"{self._get_name()}: ", end="")
        for token in self.chat.generate_assistant_reply_stepped():
            yield token
    
    def _get_multiline_input(self):
        lines = []
        
        # Read the first line normally
        first_line = input()
        lines.append(first_line)
        
        # Check if there's more input waiting in the buffer
        while True:
            # For Unix-like systems (Linux, macOS)
            if hasattr(select, 'select'):
                # Check if there's data waiting to be read
                rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
                if rlist:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                else:
                    break
            # For Windows
            else:
                try:
                    # Try to read another line with a very short timeout
                    import msvcrt
                    if msvcrt.kbhit():
                        line = input()
                        lines.append(line)
                    else:
                        break
                except:
                    # If we can't check for input, just try to read
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
        
        return '\n'.join(lines)
    
    def start_conversation(self, incremental=True):
        InputManager.system_message("Puoi iniziare a conversare con l'LLM!")
        InputManager.system_message("Scrivi 'esci' per terminare.")
        InputManager.system_message("Scrivi 'stats' per vedere le statistiche.")
        InputManager.system_message("Scrivi 'clear' per cancellare il contesto.")
    
        try:
            while True:
                # Mostra il prompt e attendi l'input dell'utente
                InputManager.show_user_prompt()
                
                # Use multiline input support
                user_input = self._get_multiline_input()
                self._send_prompt_to_llm(user_input)
    
                # Se l'utente ha scritto "esci" o "exit" o "quit" allora termina la conversazione
                if InputManager.is_exit_word(self._prompt):
                    InputManager.system_message("Conversazione terminata.")
                    break
    
                if InputManager.is_clear_context_word(self._prompt):
                    self._reset_chat()
                    continue
    
                if InputManager.is_stats_word(self._prompt):
                    self._show_stats()
                    continue
    
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
        except KeyboardInterrupt:
            print()
            InputManager.system_message("Conversazione terminata.")
        except Exception as e:
            if isinstance(e, EOFError):
                print()
                InputManager.system_message("Conversazione terminata.")
            else:
                InputManager.error(f"Si è verificato un errore: {e}")

    def _reset_chat(self):
        self.chat.reset_chat(keep_system=True)
        self._show_llm_response("Conversazione resettata: non ricordo più nulla :(")

    def _show_stats(self):
        InputManager.system_message(f"  token usati: {self.chat.tokens_used()}")
        InputManager.system_message(f"  token rimanenti: {self.chat.context_available()}")
