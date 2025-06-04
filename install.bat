@echo off
setlocal

set MODELS_DIR=models
set MODEL_FILE_NAME=Qwen3-4B-Q4_K_M.gguf
set MODEL_URL=https://huggingface.co/unsloth/Qwen3-4B-GGUF/resolve/main/%MODEL_FILE_NAME%

set TOTAL_MODEL_PATH=%MODELS_DIR%\%MODEL_FILE_NAME%

REM Controlla se il file esiste già
if not exist "%TOTAL_MODEL_PATH%" (
    echo Downloading model %MODEL_FILE_NAME%...
    mkdir "%MODELS_DIR%" 2>nul
    curl -L -o "%TOTAL_MODEL_PATH%" "%MODEL_URL%"
    echo Model %MODEL_FILE_NAME% downloaded successfully.
) else (
    echo Model %MODEL_FILE_NAME% was already downloaded.
)

echo Bye ;)
endlocal
