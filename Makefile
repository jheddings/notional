# Makefile for notional

BASEDIR ?= $(PWD)
APPNAME ?= notional
SRCDIR ?= $(BASEDIR)/src/$(APPNAME)
DISTDIR ?= $(BASEDIR)/dist
DOCSDIR ?= $(BASEDIR)/docs

WITH_VENV = poetry run

################################################################################
.PHONY: all

all: build docs test

################################################################################
.PHONY: build

build: preflight test
	poetry build

################################################################################
.PHONY: docs

docs:
	$(WITH_VENV) mkdocs build

################################################################################
.PHONY: publish

publish: build
	poetry publish

################################################################################
.PHONY: preflight

preflight: test
	$(WITH_VENV) pre-commit run --all-files --verbose

################################################################################
.PHONY: test

test:
	poetry install
	$(WITH_VENV) coverage run "--source=$(SRCDIR)" -m \
		pytest --verbose "$(BASEDIR)/tests"
	$(WITH_VENV) coverage report

################################################################################
.PHONY: coverage

coverage: test
	$(WITH_VENV) coverage html

################################################################################
.PHONY: scrub-vcr

scrub-vcr:
	rm -Rf "$(BASEDIR)/tests/cassettes"

################################################################################
.PHONY: venv

venv:
	poetry install --no-root
	$(WITH_VENV) pre-commit install --install-hooks --overwrite

################################################################################
.PHONY: clean

clean:
	rm -f "$(SRCDIR)/*.pyc"
	rm -f "$(SRCDIR)/examples/*.pyc"
	rm -Rf "$(SRCDIR)/__pycache__"
	rm -Rf "$(BASEDIR)/tests/__pycache__"
	rm -f "$(BASEDIR)/.coverage"
	rm -Rf "$(BASEDIR)/.pytest_cache"
	rm -Rf "$(BASEDIR)/build"
	rm -Rf "$(BASEDIR)/notional.egg-info"

################################################################################
.PHONY: clobber

# TODO remove poetry env

clobber: clean scrub-vcr
	$(WITH_VENV) pre-commit uninstall
	rm -Rf "$(DISTDIR)"
	rm -Rf "$(BASEDIR)/site"
	rm -Rf "$(BASEDIR)/htmlcov"
