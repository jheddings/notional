# Makefile for notional

BASEDIR ?= $(PWD)
APPNAME ?= notional
SRCDIR ?= $(BASEDIR)/$(APPNAME)
DISTDIR ?= $(BASEDIR)/dist
VENVDIR ?= $(BASEDIR)/.venv

SOURCES = "$(SRCDIR)" "$(BASEDIR)/examples" "$(BASEDIR)/tests"

# TODO make configurable for real publishing...
#TWINE_REPO ?= --repository-url https://test.pypi.org/legacy/

################################################################################
.PHONY: all

all: build test

################################################################################
.PHONY: build

build: venv-configured preflight test
	python3 setup.py sdist bdist_wheel

################################################################################
.PHONY: publish

publish: build
	twine upload $(TWINE_REPO) $(DISTDIR)/*

################################################################################
.PHONY: preflight

preflight: venv-configured test
	isort --profile black $(SOURCES)
	black $(SOURCES)
	flake8 --ignore=E266,E402,E501 $(SOURCES)

################################################################################
.PHONY: test

test: venv-configured
	python3 -m unittest discover -v -s "$(BASEDIR)/tests"

################################################################################
.PHONY: stats

stats:
	cloc $(SOURCES)

################################################################################
.PHONY: venv

venv: requirements/core.txt requirements/dev.txt
	python3 -m venv --prompt "$(APPNAME)" "$(VENVDIR)"
	"$(BASEDIR)/.venv/bin/pip3" install --upgrade pip
	"$(BASEDIR)/.venv/bin/pip3" install -r requirements/core.txt
	"$(BASEDIR)/.venv/bin/pip3" install -r requirements/dev.txt

################################################################################
.PHONY: venv-configured

venv-configured:
ifneq ($(VIRTUAL_ENV), $(VENVDIR))
	$(error Must use venv !!)
endif

################################################################################
.PHONY: clean

clean:
	rm -f "$(SRCDIR)/*.pyc"
	rm -f "$(SRCDIR)/examples/*.pyc"
	rm -Rf "$(SRCDIR)/__pycache__"
	rm -Rf "$(BASEDIR)/tests/__pycache__"
	rm -Rf "$(BASEDIR)/build"
	rm -Rf "$(BASEDIR)/notional.egg-info"

################################################################################
.PHONY: clobber

# TODO deactivate first
clobber: clean
	rm -Rf "$(BASEDIR)/dist"
	rm -Rf "$(BASEDIR)/.venv"
