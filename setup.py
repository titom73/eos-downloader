#!/usr/bin/python
# coding: utf-8 -*-

from setuptools import setup
from pathlib import Path
import eos_downloader


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="eos_downloader",
    version="{}".format(eos_downloader.__version__),
    python_requires=">=3.8",
    packages=['eos_downloader'],
    scripts=["bin/eos-download", "bin/cvp-upload"],
    install_requires=required,
    include_package_data=True,
    url="https://github.com/titom73/arista-downloader",
    license="APACHE",
    author="{}".format(eos_downloader.__author__),
    author_email="{}".format(eos_downloader.__email__),
    long_description=long_description,
    long_description_content_type='text/markdown'
)
