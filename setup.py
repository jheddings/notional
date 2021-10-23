import os

from setuptools import setup, find_packages

# used from pip's setup.py:
# https://github.com/pypa/pip/blob/main/setup.py

def read_file(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read_file(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


requirements = ["notion-client>=0.7", "pydantic>=1.8.2"]

setup(
    name="notional",
    version=get_version("notional/version.py"),
    author="Jason Heddings",
    author_email="jheddings@gmail.com",
    description="An high-level interface for the Notion SDK.",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/jheddings/notional/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
