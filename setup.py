#!/usr/bin/python
# coding: utf-8 -*-

import shutil
from setuptools import setup
import eos_downloader

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="eos_downloader",
    version=eos_downloader.__version__,
    python_requires=">=3.6",
    packages=['eos_downloader'],
    scripts=["bin/arista-download", "bin/eos-download", "bin/cvp-upload"],
    install_requires=required,
    include_package_data=True,
    url="https://github.com/titom73/arista-downloader",
    license="APACHE",
    # author="{}".format(inetsixEve.__author__),
    # author_email="{}".format(inetsixEve.__email__),
    description=long_description,
)
