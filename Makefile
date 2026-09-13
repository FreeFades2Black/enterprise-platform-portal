.PHONY: all build serve test clean

all: build

build:
	python -m mkdocs build --strict

serve:
	python -m mkdocs serve

test: build
	@echo "[+] Enterprise Platform Portal build verified successfully."

clean:
	rm -rf site/
