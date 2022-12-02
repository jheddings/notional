# notional #

[![PyPI](https://img.shields.io/pypi/v/notional.svg)](https://pypi.org/project/notional)
[![LICENSE](https://img.shields.io/github/license/jheddings/notional)](LICENSE)
[![Style](https://img.shields.io/badge/style-black-black)](https://github.com/ambv/black)

A high level interface and object model for the Notion SDK.  This is loosely modeled
after concepts found in [SQLAlchemy](http://www.sqlalchemy.org) and
[MongoEngine](http://mongoengine.org).  Built on the excellent
[notion-sdk-py](https://github.com/ramnes/notion-sdk-py) library, this module provides
higher-level access to the API.

> :warning: **Work In Progress**: The interfaces in this module are still in development
and are likely to change.  Furthermore, documentation is pretty sparse so use at your
own risk!

That being said, if you do use this library, please drop me a message!

## Installation ##

Install the most recent release using PyPi:

```shell
pip install notional
```

*Note:* it is recommended to use a virtual environment (`venv`) for installing libraries
to prevent conflicting dependency versions.

## Usage ##

Connect to the API using an integration token or an OAuth access token:

```python
import notional

notion = notional.connect(auth=AUTH_TOKEN)

# ¡¡ fun & profit !!
```

## Getting Help ##

If you are stuck, the best place to start is the
[Discussion](https://github.com/jheddings/notional/discussions) area.  Use this also as
a resource for asking questions or providing general suggestions.

### Known Issues ###

See [Issues](https://github.com/jheddings/notional/issues) on github.

### Feature Requests ###

See [Issues](https://github.com/jheddings/notional/issues) on github.

## Contributing ##

I built this module so that I could interact with Notion in a way that made sense to
me.  Hopefully, others will find it useful.  If someone is particularly passionate about
this area, I would be happy to consider other maintainers or contributors.

Any pull requests or other submissions are welcome.  As most open source projects go, this
is a side project.  Large submissions will take time to review for acceptance, so breaking
them into smaller pieces is always preferred.  Thanks in advance!

To get started, please read the full [contribution guide](.github/CONTRIBUTING.md).
