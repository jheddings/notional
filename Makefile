# Makefile for Notional

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= $(shell grep -m1 '^name' "$(BASEDIR)/pyproject.toml" | sed -e 's/name.*"\(.*\)"/\1/')
APPVER ?= $(shell grep -m1 '^version' "$(BASEDIR)/pyproject.toml" | sed -e 's/version.*"\(.*\)"/\1/')

VENV := poetry run
PY := $(VENV) python3

################################################################################
.PHONY: all

all: venv build test

################################################################################
.PHONY: build-pkg

build-pkg: venv preflight test
	poetry --no-interaction build

################################################################################
.PHONY: build-docs

build-docs: venv
	$(VENV) mkdocs build

################################################################################
.PHONY: build

build: build-pkg

################################################################################
.PHONY: github-reltag

github-reltag: build test
	git tag "v$(APPVER)" main
	git push origin "v$(APPVER)"

################################################################################
.PHONY: publish-pypi

publish-pypi: venv preflight test build-pkg
	poetry publish --no-interaction

################################################################################
.PHONY: publish-docs

publish-docs: venv
	$(VENV) mkdocs gh-deploy --force

################################################################################
.PHONY: publish

publish: publish-pypi publish-docs

################################################################################
.PHONY: release

release: publish github-reltag

################################################################################
.PHONY: run

run: venv
	$(PY) -m notional

################################################################################
.PHONY: preflight

preflight: venv
	$(VENV) pre-commit run --all-files --verbose

################################################################################
.PHONY: test

test: venv preflight
	$(VENV) pytest $(BASEDIR)/tests --vcr-record=once

################################################################################
.PHONY: test-coverage

test-coverage: venv
	$(VENV) coverage run "--source=$(SRCDIR)" -m \
		pytest $(BASEDIR)/tests --vcr-record=once

################################################################################
.PHONY: coverage-txt

coverage-txt: venv test-coverage
	$(VENV) coverage report

################################################################################
.PHONY: coverage-html

coverage-html: venv test-coverage
	$(VENV) coverage html

################################################################################
.PHONY: venv

venv:
	poetry install --sync
	$(VENV) pre-commit install --install-hooks --overwrite

################################################################################
.PHONY: clean

clean:
	rm -f "$(BASEDIR)/.coverage"
	rm -Rf "$(BASEDIR)/.pytest_cache"
	find "$(BASEDIR)" -name "*.pyc" -print | xargs rm -f
	find "$(BASEDIR)" -name '__pycache__' -print | xargs rm -Rf

################################################################################
.PHONY: clobber

clobber: clean
	rm -Rf "$(BASEDIR)/htmlcov"
	rm -Rf "$(BASEDIR)/dist"
	rm -Rf "$(BASEDIR)/site"
	rm -Rf "$(BASEDIR)/.venv"
