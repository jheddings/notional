# Makefile for Notional

# use a local.env file if it exists
-include local.env

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= $(shell grep -m1 '^name' "$(BASEDIR)/pyproject.toml" | sed -e 's/name.*"\(.*\)"/\1/')
APPVER ?= $(shell grep -m1 '^version' "$(BASEDIR)/pyproject.toml" | sed -e 's/version.*"\(.*\)"/\1/')

WITH_VENV := poetry run

export

################################################################################
.PHONY: all

all: venv preflight build

################################################################################
.PHONY: venv

venv:
	poetry install --sync
	$(WITH_VENV) pre-commit install --install-hooks --overwrite

################################################################################
.PHONY: build-dist

build-dist: preflight
	poetry --no-interaction build

################################################################################
.PHONY: build-docs

build-docs: venv
	$(WITH_VENV) mkdocs build

################################################################################
.PHONY: build

build: build-dist

################################################################################
.PHONY: github-reltag

github-reltag: preflight
	git tag "v$(APPVER)" main
	git push origin "v$(APPVER)"

################################################################################
.PHONY: publish-pypi

publish-pypi: preflight build-dist
	poetry publish --no-interaction

################################################################################
.PHONY: publish-docs

publish-docs: venv
	$(WITH_VENV) mkdocs gh-deploy --force

################################################################################
.PHONY: publish

publish: publish-pypi publish-docs

################################################################################
.PHONY: release

release: publish github-reltag

################################################################################
.PHONY: run

run: venv
	$(WITH_VENV) python3 -m notional

################################################################################
.PHONY: static-checks

static-checks: venv
	$(WITH_VENV) pre-commit run --all-files --verbose

################################################################################
.PHONY: unit-tests

unit-tests: venv
	$(WITH_VENV) coverage run "--source=$(SRCDIR)" -m \
		pytest $(BASEDIR)/tests --vcr-record=once

################################################################################
.PHONY: coverage-report

coverage-report: venv unit-tests
	$(WITH_VENV) coverage report

################################################################################
.PHONY: coverage-html

coverage-html: venv unit-tests
	$(WITH_VENV) coverage html

################################################################################
.PHONY: coverage

coverage: coverage-report coverage-html

################################################################################
.PHONY: preflight

preflight: static-checks unit-tests coverage-report

################################################################################
.PHONY: reset-vcr

reset-vcr:
	rm -Rf "$(BASEDIR)/tests/cassettes"

################################################################################
.PHONY: clean

clean:
	rm -f "$(BASEDIR)/.coverage"
	rm -Rf "$(BASEDIR)/.pytest_cache"
	find "$(BASEDIR)" -name "*.pyc" -print | xargs rm -f
	find "$(BASEDIR)" -name '__pycache__' -print | xargs rm -Rf

################################################################################
.PHONY: clobber

clobber: clean reset-vcr
	rm -Rf "$(BASEDIR)/htmlcov"
	rm -Rf "$(BASEDIR)/dist"
	rm -Rf "$(BASEDIR)/site"
	rm -Rf "$(BASEDIR)/.venv"
