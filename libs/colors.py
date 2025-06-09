
class Colors:
    # Codici ANSI per i colori del testo
    T_BLACK     = "\u001B[30m"
    T_RED       = "\u001B[31m"
    T_GREEN     = "\u001B[32m"
    T_YELLOW    = "\u001B[33m"
    T_BLUE      = "\u001B[34m"
    T_MAGENTA   = "\u001B[35m"
    T_CYAN      = "\u001B[36m"
    T_WHITE     = "\u001B[37m"
    T_ORANGE    = "\u001B[38;5;208m"
    T_RESET     = "\u001B[39m"
    
    # Codici ANSI per lo sfondo
    BG_BLACK    = "\u001B[40m"
    BG_RED      = "\u001B[41m"
    BG_GREEN    = "\u001B[42m"
    BG_YELLOW   = "\u001B[43m"
    BG_BLUE     = "\u001B[44m"
    BG_MAGENTA  = "\u001B[45m"
    BG_CYAN     = "\u001B[46m"
    BG_WHITE    = "\u001B[47m"
    BG_ORANGE   = "\u001B[48;5;208m"
    BG_RESET    = "\u001B[49m"
    
    # Altri effetti
    T_BG_RESET  = "\u001B[00m"
    T_BOLD      = "\u001B[01m"
    T_BOLD_OFF  = "\u001B[22m"
    T_BLINK     = "\u001B[05m"
    T_BLINK_OFF = "\u001B[25m"

    @staticmethod
    def _color(color, string):
        # Applica il colore e resetta a fine stringa
        return f"{color}{string}{Colors.T_BG_RESET}"

    @staticmethod
    def blink(string):
        return f"{Colors.T_BLINK}{string}{Colors.T_BLINK_OFF}"

    @staticmethod
    def black(string):
        return Colors._color(Colors.T_BLACK, string)

    @staticmethod
    def red(string):
        return Colors._color(Colors.T_RED, string)

    @staticmethod
    def green(string):
        return Colors._color(Colors.T_GREEN, string)

    @staticmethod
    def yellow(string):
        return Colors._color(Colors.T_YELLOW, string)

    @staticmethod
    def blue(string):
        return Colors._color(Colors.T_BLUE, string)

    @staticmethod
    def magenta(string):
        return Colors._color(Colors.T_MAGENTA, string)

    @staticmethod
    def cyan(string):
        return Colors._color(Colors.T_CYAN, string)

    @staticmethod
    def white(string):
        return Colors._color(Colors.T_WHITE, string)
