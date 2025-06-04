from llama_cpp import Llama, LlamaGrammar

from .input_manager import InputManager


class Message:
    def __init__(self, agent: str, content: str) -> None:
        self.agent = agent
        self.content = content

    def __repr__(self) -> str:
        return f'<{self.agent}> {self.content}'


class Chat:

    SYSTEM_KEY = 'system'
    ASSISTANT_KEY = 'assistant'
    USER_KEY = 'user'

    CLEAR_CURRENT_LINE = '\33[2K\r'
    CHARSET = 'UTF-8'

    def __init__(
            self,
            model: Llama,
            n_generate: int,
            bot: str = None,
            eos: str = '<|im_end|>',
            temperature: float = 0.8,
            top_p: float = 0.9,
            top_k: int = 40,
            agent_prefixes: dict[str, str] = None,
            agent_names: dict[str, str] = None,
            debug: bool = False,
            system_prompt: str = "",
            think: bool = False
    ) -> None:
        """
        Crea un nuovo oggetto Chat

        @param model: l'oggetto llama che rappresenta il modello
        @param bot: il token che inizia la chat
        @param eos: il token che termina un singolo turno di chat
        @param n_generate: il numero massimo di token generati dal modello in un singolo turno
        @param temperature: la temperatura usata per l'inferenza del modello
        @param top_p: il parametro top_p usato per l'inferenza
        @param top_k: il parametro top_k usato per l'inferenza
        @param agent_prefixes: i token usati per marcare il nome di un agente
        @param agent_names: dizionario con i nomi per: system, assistant, user
        @param debug: se abilitare o meno le informazioni di debug
        """
        self.model = model
        self.bot = bot
        self.eos = eos
        self.n_generate = n_generate
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.agent_prefixes = agent_prefixes if agent_prefixes is not None else {
            self.SYSTEM_KEY: '<|im_start|>system',
            self.ASSISTANT_KEY: '<|im_start|>assistant',
            self.USER_KEY: '<|im_start|>user'
        }
        self.agent_names = agent_names if agent_names is not None else {
            self.SYSTEM_KEY: 'system',
            self.ASSISTANT_KEY: 'assistant',
            self.USER_KEY: 'user'
        }
        self.system_prompt = system_prompt
        self.debug = debug

        self.eos_token = self.tokenize_text(self.eos, add_bos=False, special=True)[0]
        self.bot_token = self.tokenize_text(self.bot, add_bos=False, special=True)[0] if self.bot and len(self.bot) > 0 else None

        self.messages: list[Message] = []
        self.tokens_cache: list[int] = []

        self.cache_initialize()

        if not think:
            self.send_message(
                agent=self.SYSTEM_KEY,
                content=(self.system_prompt + '\n\n/no_think').strip())


    def generate_assistant_reply(self, grammar: LlamaGrammar | None = None) -> tuple[str, int]:
        """
        Ottiene una risposta dal modello (presumibilmente dopo un messaggio dell'utente) come stringa completa.

        @param grammar: la grammatica usata per vincolare l'output del modello
        @return: il testo della risposta e il numero di token rimanenti nel contesto
        """
        self.cache_append_header(agent=self.ASSISTANT_KEY)

        reply = ''
        n_reply_tokens = 0
        for token in self.model.generate(tokens=self.tokens_cache, temp=self.temperature, top_p=self.top_p, top_k=self.top_k, grammar=grammar):
            self.check_context_overflow()  # Verifica che il contesto non sia stato superato
            if token == self.model.token_eos() or token == self.eos_token:  # Verifica la terminazione EOS
                self.tokens_cache.append(self.eos_token)
                break
            if n_reply_tokens >= self.n_generate:  # Verifica se il modello ha generato più token del dovuto
                self.tokens_cache.append(self.eos_token)
                break

            self.tokens_cache.append(token)
            n_reply_tokens += 1
            reply += self.detokenize_tokens([token])

            interrupt, reply = self.check_eos_failure(reply)
            if interrupt: break
            interrupt, reply = self.check_model_impersonation(reply, self.USER_KEY)
            if interrupt: break
            interrupt, reply = self.check_model_impersonation(reply, self.SYSTEM_KEY)
            if interrupt: break

        self.add_message(self.ASSISTANT_KEY, reply)

        return reply, self.context_available()


    def generate_assistant_reply_stepped(self, grammar: LlamaGrammar | None = None):
        """
        Ottiene una risposta dal modello come flusso di token.

        @param grammar: la grammatica usata per vincolare l'output del modello
        @return: il singolo token (già detokenizzato) generato
        """
        self.cache_append_header(agent=self.ASSISTANT_KEY)

        reply = ''
        n_reply_tokens = 0
        for token in self.model.generate(tokens=self.tokens_cache, temp=self.temperature, top_p=self.top_p, top_k=self.top_k, grammar=grammar):
            self.check_context_overflow()
            if token == self.model.token_eos() or token == self.eos_token:
                self.tokens_cache.append(self.eos_token)
                yield '\n'
                break
            if n_reply_tokens >= self.n_generate:
                self.tokens_cache.append(self.eos_token)
                yield '\n'
                break

            self.tokens_cache.append(token)
            n_reply_tokens += 1
            new_text = self.detokenize_tokens([token])
            reply += new_text

            interrupt, reply = self.check_eos_failure(reply)
            if interrupt:
                n_char_to_delete = len(self.eos) - 1
                back_str = '\b' * n_char_to_delete
                empty_str = ' ' * n_char_to_delete
                yield back_str + empty_str + '\n'
                break
            interrupt, reply = self.check_model_impersonation(reply, self.USER_KEY)
            if interrupt:
                yield self.CLEAR_CURRENT_LINE
                break
            interrupt, reply = self.check_model_impersonation(reply, self.SYSTEM_KEY)
            if interrupt:
                yield self.CLEAR_CURRENT_LINE
                break

            yield new_text

        self.add_message(self.ASSISTANT_KEY, reply)


    def send_message(self, agent: str, content: str) -> int:
        """
        Aggiunge un messaggio al contesto della chat

        @param agent: l'agente che ha inviato il messaggio
        @param content: il contenuto del messaggio
        @return: il contesto disponibile dopo l'aggiunta
        """
        new_message = self.add_message(agent, content)
        self.cache_append_message(new_message)

        return self.context_available()


    def add_message(self, agent: str, content: str) -> Message:
        """
        Crea un nuovo messaggio e lo aggiunge alla lista dei messaggi salvati.
        NON aggiunge il contenuto al contesto.

        @param agent: l'agente che ha inviato il contenuto
        @param content: il contenuto del messaggio
        @return: il messaggio creato
        """
        new_message = Message(agent=agent, content=content)
        self.messages.append(new_message)

        return new_message


    def check_eos_failure(self, reply: str) -> tuple[bool, str]:
        """
        Verifica se il modello ha prodotto un token EOS non correttamente codificato.

        @param reply: la risposta dell'assistente
        @return: una tupla `(interruzione_rilevata, risposta_pulita)`
        """
        interrupt = False
        if self.eos in reply[-(len(self.eos)+1):]:
            if self.debug: print(f'[DEBUG] Rilevato escape EOS: {reply[-len(self.eos):]}')
            reply = reply[:-len(self.eos)]
            interrupt = True

        return interrupt, reply


    def check_model_impersonation(self, reply: str, agent: str) -> tuple[bool, str]:
        """
        Verifica se il modello ha cercato di impersonare l'utente o il sistema.

        @param reply: la risposta dell'assistente
        @param agent: l'agente che il modello potrebbe aver impersonato
        @return: una tupla `(impersonificazione_rilevata, risposta_pulita)`
        """
        interrupt = False
        if self.agent_prefixes[agent] in reply:
            if self.debug: print(f'[DEBUG] Rilevata impersonificazione di {agent}')
            reply = reply.split(self.agent_prefixes[agent])[0].strip()
            interrupt = True

        return interrupt, reply


    def cache_initialize(self) -> None:
        """
        Inizializza il contesto e riaggiunge eventualmente il BOS
        """
        self.tokens_cache = []
        if self.bot_token:
            self.tokens_cache.append(self.bot_token)


    def cache_append_header(self, agent: str) -> None:
        """
        Aggiunge l'intestazione di partenza per un agente al contesto

        @param agent: l'agente a cui appartiene l'intestazione
        """
        header = f'{self.agent_prefixes[agent]}'
        self.tokens_cache += self.tokenize_text(header)


    def cache_append_message(self, message: Message) -> None:
        """
        Aggiunge un messaggio al contesto in forma tokenizzata

        @param message: il messaggio da aggiungere
        """
        round_text = f'{self.agent_prefixes[message.agent]}{message.content}{self.eos}'
        self.tokens_cache += self.tokenize_text(round_text)


    def cache_rebuild(self) -> None:
        """
        Ricostruisce la cache usando la lista di messaggi salvati
        """
        self.cache_initialize()

        for msg in self.messages:
            self.cache_append_message(msg)


    def reset_chat(self, keep_system: bool = False) -> None:
        """
        Reimposta la chat, cancellando contesto e messaggi

        @param keep_system: se mantenere i messaggi di sistema nel contesto
        """
        self.cache_initialize()

        if keep_system:
            self.messages = [msg for msg in self.messages if msg.agent == self.SYSTEM_KEY]

            for msg in self.messages:
                self.cache_append_message(msg)
        else:
            self.messages = []


    def detokenize_tokens(self, tokens: list[int]) -> str:
        """
        Detokenizza una lista di token in una stringa

        @param tokens: la lista di token
        """
        errors_strategy = 'ignore'
        try:
            return self.model.detokenize(tokens).decode(self.CHARSET, errors=errors_strategy)
        except Exception as e:
            InputManager.error('errore durante la detokenizzazione di:', tokens)
            exit(1)


    def tokenize_text(self, text: str, add_bos: bool = False, special: bool = True) -> list[int]:
        """
        Tokenizza una stringa in una lista di token

        @param text: il testo da tokenizzare
        @param add_bos: se aggiungere il token BOS
        @param special: se codificare i token speciali come tali
        @return: la lista di token
        """
        try:
            return self.model.tokenize(text=bytes(text, self.CHARSET), add_bos=add_bos, special=special)
        except Exception as e:
            InputManager.error('errore durante la tokenizzazione di:', text)
            exit(1)


    def check_context_overflow(self):
        """
        Verifica se il contesto disponibile è stato superato
        """
        if self.context_available() <= 0:
            InputManager.error('contesto superato.')
            exit(1)


    def print_stats(self):
        """
        Stampa alcune statistiche della chat
        """
        InputManager.system_message(f'token usati: {self.tokens_used()}')
        InputManager.system_message(f'token rimanenti: {self.context_available()}')


    def context_available(self) -> int:
        """
        Restituisce il numero di token ancora disponibili nel contesto

        @return: numero di token disponibili
        """
        return self.model.n_ctx() - self.tokens_used()


    def tokens_used(self) -> int:
        """
        Restituisce il numero di token usati finora nel contesto

        @return: numero di token usati
        """
        return len(self.tokens_cache)


    def get_raw_chat(self) -> str:
        """
        Restituisce il testo grezzo della chat

        @return: la chat completa sotto forma di stringa
        """
        return self.detokenize_tokens(self.tokens_cache)
