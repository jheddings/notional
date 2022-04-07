# Contributing #

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
