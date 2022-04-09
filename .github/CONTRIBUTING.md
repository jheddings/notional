# Contributing #

## Quick Start ##

1. Fork the `notional` repository into your account and clone a local working copy.

2. Create a new feature branch for your changes.

3. Set up a local environment.

    1. Create a virtual environment:

       ```shell
       python3 -m venv .venv
       source .venv/bin/activate
       ```

    2. Install dependencies:

       ```shell
       pip3 install -r requirements/core.txt
       pip3 install -r requirements/dev.txt
       ```

    3. Install `pre-commit` hooks:

       ```shell
       pre-commit install
       ```

   Alternatively, use `make devenv` to set this all up for you.

4. Follow the standards enforced by the tools.  At any time, you may use the
   `preflight` target to run the unit tests and code checks.

5. Provide tests for new code and ensure they are passing.

6. Submit a pull request with your changes.

## Pull Requests ##

Pull requests are highly encouraged!  Please make sure the PR passes `pre-commit`
prior to submission.

## Coding Standards ##

Notional uses standard Python coding practices.

### Style ###

All code must be formatted using `black`.

Additionally, all `import` statements will be sorted according to `isort`.

### Static Analysis ###

Code will be scanned using `flake8`.

## Unit Tests ##

Where practical, stand-alone unit tests ae strongly encouraged.  In the future,
code coverage may be enforced for new commits.

If it is not practical to develop a unit test, evidence of working code must
be provided in the pull request.

## Submitting Issues & Requests ##

Please review the open issues and feature requests.  This is a great place to start if
you are looking for ways to contribute!

### Known Issues ###

See [Issues](https://github.com/jheddings/notional/issues) on github.

### Feature Requests ###

See [Issues](https://github.com/jheddings/notional/issues) on github.
