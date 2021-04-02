from setuptools import setup

import ziggurat

with open("README.md") as f:
    long_desc = f.read()

setup(
    name="ziggurat",
    version=ziggurat.__version__,
    author=ziggurat.__author__,
    author_email=ziggurat.__email__,
    description=ziggurat.__doc__,
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/rsiemens/ziggurat/",
    packages=["ziggurat"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
