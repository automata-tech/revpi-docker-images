all: build
.PHONY: all

build: install
	pipenv run ./build.py
.PHONY: build

push: install
	pipenv run ./build.py --push
.PHONY: push

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
