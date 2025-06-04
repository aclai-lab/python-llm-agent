@echo off
setlocal

set "MODELS_DIR=models"
set "MODEL_NAME=Qwen3-4B"
set "MODEL_FILE_NAME=%MODEL_NAME%-Q4_K_M.gguf"
set "MODEL_URL=https://huggingface.co/unsloth/%MODEL_NAME%-GGUF/resolve/main/%MODEL_FILE_NAME%"

rem Function-like section to download a model
call :download "%MODEL_FILE_NAME%" "%MODEL_URL%"

echo Bye ;)
goto :eof

:download
set "MODEL_FILE_NAME=%~1"
set "MODEL_URL=%~2"
set "TOTAL_MODEL_PATH=%MODELS_DIR%\%MODEL_FILE_NAME%"

if not exist "%TOTAL_MODEL_PATH%" (
    echo Downloading model %MODEL_FILE_NAME%...
    if not exist "%MODELS_DIR%" (
        mkdir "%MODELS_DIR%"
    )
    curl -L -o "%TOTAL_MODEL_PATH%" "%MODEL_URL%"
    echo Model %MODEL_FILE_NAME% downloaded successfully.
) else (
    echo Model %MODEL_FILE_NAME% was already downloaded.
)
goto :eof
