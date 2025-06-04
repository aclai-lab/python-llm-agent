#!/bin/bash

MODELS_DIR="models"
MODEL_NAME="Qwen3-4B"
MODEL_FILE_NAME="${MODEL_NAME}-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/unsloth/${MODEL_NAME}-GGUF/resolve/main/$MODEL_FILE_NAME"

# Function to download a model
download() {
    local model_file_name="$1"
    local total_model_path="$MODELS_DIR/$1"
    local model_url="$2"

    if [ ! -f "$total_model_path" ]; then
        echo "Downloading model $model_file_name..."
        mkdir -p "$MODELS_DIR"
        curl -L -o "$total_model_path" "$model_url"
        echo "Model $model_file_name downloaded successfully."
    else
        echo "Model $model_file_name was already downloaded."
    fi
}

# Download model
download "$MODEL_FILE_NAME" "$MODEL_URL"

echo "Bye ;)"
