import os

from setuptools import setup, find_packages

with open("README.md", "r") as fp:
    readme = fp.read()

requirements = ["notion-client>=0.5"]

# https://github.com/techtonik/setuptools/commit/1c007d24f2733efac6ea5e6eda5e9b0319c38bf5
def get_version(path, field="__version__"):
     version_file = os.path.abspath(path)
     if type(field) is not bytes:
         field = field.encode("utf-8")
     for line in open(version_file, "rb"):
         if line.startswith(field):
             _, value = line.split(b"=")
             version = value.strip(b" \'\"").decode()
             return version

setup(
    name="notional",
    version=get_version("notional/__init__.py"),
    author="Jason Heddings",
    author_email="jheddings@gmail.com",
    description="An object model for the Notion SDK.",
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
