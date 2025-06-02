# Laboratorio LLM

Questo laboratorio permette agli studenti di esplorare un modello linguistico locale (LLM) usando Python e `llama.cpp`. Il modello scelto è **Qwen3-0.6B** in formato `GGUF`, adatto a computer con risorse limitate.

## 📦 Requisiti

- Sistema operativo: Linux
- Python ≥ 3.8
- Accesso a terminale
- Modello GGUF scaricato in `./models/qwen/Qwen3-0.6B-Q8_0.gguf`

## 🔧 Installazione

1. Crea un ambiente virtuale (opzionale ma consigliato)
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

3. Verifica di aver scaricato il modello in:
   ```
   ./models/qwen/Qwen3-0.6B-Q8_0.gguf
   ```

   Puoi trovare i modelli compatibili su: [https://huggingface.co/TheBloke](https://huggingface.co/TheBloke)

## 🚀 Avvio

Esegui il programma:

```bash
python main.py
```

## 🧠 Cosa puoi fare

* Conversa con l'LLM in italiano o inglese
* Modifica il codice Python per cambiare la personalità dell'LLM
* Aggiungi salvataggio della chat su file
* Usa prompt creativi o tematici

## 🧪 Idee per esercizi

* Crea un assistente per lo studio
* Simula una chat con uno scrittore o personaggio storico
* Analizza come l’LLM risponde a prompt ambigui o specifici
