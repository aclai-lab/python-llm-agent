
VENV_DIR = venv

all: main

main: $(SRCS)
	@echo "========= INSTALLAZIONE LLM ========="
	@./install.sh
	@echo "========= CREAZIONE AMBIENTE DI SVILUPPO ========="
	@pip install --user virtualenv --break-system-packages
	@python3 -m virtualenv $(VENV_DIR)
	@echo "========= INSTALLAZIONE DIPENDENZE PYTHON ========="
	@./$(VENV_DIR)/bin/pip install -r requirements.txt

run:
	@./$(VENV_DIR)/bin/python3 main.py
