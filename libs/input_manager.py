import sys
import atexit
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
    def prompt():
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
    def _is_exit_word(word: str):
        """Verifica se una parola è una parola chiave per terminare la conversazione."""
        return word.lower() in ["esci", "exit", "quit"]

