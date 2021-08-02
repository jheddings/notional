from setuptools import setup, find_packages

with open("README.md", "r") as fp:
    readme = fp.read()

requirements = ["notion-client>=0.4"]

setup(
    name="notional",
    version="0.0.1",
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
