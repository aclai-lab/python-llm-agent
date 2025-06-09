# Laboratorio LLM

Questo laboratorio permette agli studenti di esplorare un modello linguistico locale (LLM) usando Python e `llama.cpp`. Il modello scelto è **Qwen3-4B** in formato `GGUF`, adatto a computer con risorse limitate.

## 📦 Requisiti

- Sistema operativo: Linux
- Python ≥ 3.8
- Accesso a terminale
- Modello GGUF scaricato in `./models/Qwen3-4B-Q4_K_M.gguf`

## 🔧 Installazione

1. crea un ambiente virtuale (opzionale ma consigliato)
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2. installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

3. verifica di aver scaricato il modello in:
   ```
   ./models/Qwen3-4B-Q4_K_M.gguf
   ```

   Puoi trovare i modelli compatibili su: [https://huggingface.co/unsloth](https://huggingface.co/unsloth)

## 🚀 Avvio

Esegui il programma:

```bash
python start_chat.py
```

## 🧠 Cosa puoi fare

- implementare il main del programma
- conversa con l'LLM in italiano o inglese
- modifica il codice Python per cambiare la personalità dell'LLM
- usa prompt creativi o tematici
   - crea un assistente per lo studio
   - simula una chat con uno scrittore o personaggio storico
   - analizza come l’LLM risponde a prompt ambigui o specifici
