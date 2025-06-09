import sys
import atexit
import select
from .colors import Colors

# Eccezione personalizzata per gli errori di tipo
class InputTypeException(Exception):
    pass

class InputManager:
    _user_name = "utente"

    @staticmethod
    def set_name(name):
        InputManager._user_name = name

    @staticmethod
    def show_user_prompt():
        """Disegna il prompt per l'utente."""
        print(Colors.green(InputManager._user_name) + ": ", end="", flush=True)

    @staticmethod
    def system_message(text, new_line=True):
        """Stampa un messaggio di sistema."""
        if text.startswith(" ") or text.startswith("\t"):
            print(text, end="", flush=True)
        else:
            print(Colors.blue("sistema") + ": " + text, end="", flush=True)

        if new_line:
            print()

    @staticmethod
    def error(text="", new_line=True):
        """Stampa un messaggio di errore."""
        print(Colors.red("errore") + ": " + text, file=sys.stderr, end="", flush=True)
        if new_line:
            print(file=sys.stderr)

    @staticmethod
    def warn(text="", new_line=True):
        """Stampa un messaggio di warning."""
        print(Colors.yellow("warning") + ": " + text, file=sys.stderr, end="", flush=True)
        if new_line:
            print(file=sys.stderr)

    @staticmethod
    def handle_interrupt():
        """Aggancia una funzione per l'arresto pulito del sistema."""
        def on_exit():
            print(Colors.blue("sistema") + ": arresto del sistema in corso...")
            print(Colors.blue("sistema") + ": il sistema è stato arrestato correttamente")

        atexit.register(on_exit)
    
    @staticmethod
    def remove_think_tokens(prompt: str):
        """Pulisce da /think e /no_think il prompt"""
        return prompt.replace("/think", "").replace("/no_think", "").strip()

    @staticmethod
    def is_exit_word(word: str):
        """Verifica se una parola è una parola chiave per terminare la conversazione."""
        return InputManager.remove_think_tokens(word).lower() in ["esci", "exit", "quit"]

    @staticmethod
    def is_stats_word(word: str):
        """Verifica se una parola è una parola chiave per mostrare le statistiche."""
        return InputManager.remove_think_tokens(word).lower() in ["statistiche", "stats"]

    @staticmethod
    def is_clear_context_word(word: str):
        """Verifica se una parola è una parola chiave per cancellare il contesto."""
        return InputManager.remove_think_tokens(word).lower() in ["clear", "clc"]
        
    @staticmethod
    def _get_multiline_input():
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
