#!/bin/bash

MODELS_DIR="models"
MODEL_FILE_NAME="Qwen3-0.6B-Q8_0.gguf"
MODEL_URL="https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/blob/main/${MODEL_FILE_NAME}"

# Start program
TOTAL_MODEL_PATH="$MODELS_DIR/$MODEL_FILE_NAME"

if [ ! -f "$TOTAL_MODEL_PATH" ]; then
    echo "Downloading model $MODEL_FILE_NAME..."
    mkdir -p "$MODELS_DIR"
    curl -L -o "$TOTAL_MODEL_PATH" "$MODEL_URL"
    echo "Model $MODEL_FILE_NAME downloaded successfully."
else
    echo "Model $MODEL_FILE_NAME was already downloaded."
fi

echo "Bye ;)"
