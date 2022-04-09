# Quick Start #

This guide should help you get up and running quickly with Notional!

## Authorization ##

Obtain an [authentication token](https://developers.notion.com/docs/authorization) from
Notion.

### Token Security ###

It is generally a best practice to read the auth token from an environment variable or
a secrets file.  To prevent accidental exposure, it is NOT recommended to save the token
in source.

## Installation ##

Install the most recent release using PyPI:

```shell
pip install notional
```

*Note:* it is recommended to use a virtual environment (`venv`) for installing libraries
to prevent conflicting dependency versions.

## Connection ##

Connect to the API using an integration token or an OAuth access token:

```python
import notional

notion = notional.connect(auth=AUTH_TOKEN)

# ¡¡ fun & profit !!
```
