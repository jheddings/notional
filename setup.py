"""Module definition for Notional."""

import os

from setuptools import find_packages, setup

# used helpers from pip's setup.py:
# https://github.com/pypa/pip/blob/main/setup.py


def read_file(rel_path: str) -> str:
    """Read the full contents of the given path, relative to this file."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    """Return the __version__ value from the given file."""
    for line in read_file(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


# TODO read from requirements/core.txt
requirements = [
    "notion-client>=0.9.0",
    "pydantic>=1.9.0",
    "html5lib>=1.1",
]

project_urls = {
    "Documentation": "https://jheddings.github.io/notional/",
}

setup(
    name="notional",
    version=get_version("notional/version.py"),
    author="Jason Heddings",
    author_email="jheddings@gmail.com",
    description="An high-level interface for the Notion SDK.",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/jheddings/notional/",
    project_urls=project_urls,
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
