# Makefile for notional

BASEDIR ?= $(PWD)
APPNAME ?= notional
SRCDIR ?= $(BASEDIR)/$(APPNAME)
DISTDIR ?= $(BASEDIR)/dist
VENVDIR ?= $(BASEDIR)/.venv

WITH_VENV = source "$(VENVDIR)/bin/activate" &&

SOURCES = "$(SRCDIR)" "$(BASEDIR)/examples" "$(BASEDIR)/tests" "$(BASEDIR)/setup.py"

################################################################################
.PHONY: all

all: build test

################################################################################
.PHONY: build

build: preflight test
	$(WITH_VENV) python3 setup.py sdist bdist_wheel

################################################################################
.PHONY: publish

publish: build
	twine upload --repository notional $(DISTDIR)/*

################################################################################
.PHONY: preflight

preflight: test
	$(WITH_VENV) pre-commit run --all-files

################################################################################
.PHONY: test

test:
	$(WITH_VENV) python3 -m unittest discover -v -s "$(BASEDIR)/tests"

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
.PHONY: devenv

devenv: venv
	$(WITH_VENV) pre-commit install

################################################################################
.PHONY: upgrade-venv

upgrade-venv:
	cat "$(BASEDIR)/requirements/core.txt" "$(BASEDIR)/requirements/dev.txt" \
		| cut -f1 -d= | xargs pip3 install --upgrade

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
	$(WITH_VENV) pre-commit uninstall
	rm -Rf "$(DISTDIR)"
	rm -Rf "$(VENVDIR)"
