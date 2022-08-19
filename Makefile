all: clean images build
.PHONY: all

images:
	./images.py
.PHONY: images

build:
	./build.py
.PHONY: build

clean:
	rm -rf images/*
.PHONY: clean

install:
	pipenv install -d
.PHONY: install

lint: install
	pipenv run black . --check
	pipenv run isort . --diff --check-only
	pipenv run flake8
	pipenv run mypy
.PHONY: lint

lint-fix: install
	pipenv run black .
	pipenv run isort .
.PHONY: lint-fix
