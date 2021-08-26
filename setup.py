import os

from setuptools import setup, find_packages
from notional.version import __version__

with open("README.md", "r") as fp:
    readme = fp.read()

requirements = ["notion-client>=0.6", "pydantic>=1.8.2"]

setup(
    name="notional",
    version=__version__,
    author="Jason Heddings",
    author_email="jheddings@gmail.com",
    description="An high-level interface for the Notion SDK.",
    long_description=readme,
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
