#!/usr/bin/python
# coding: utf-8 -*-

from setuptools import setup, find_packages
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
    packages=find_packages(),
    include_package_data=True,
    scripts=["bin/eos-download", "bin/cvp-upload"],
    entry_points={
        'console_scripts': [
            'ardl=eos_downloader.cli.cli:cli',
            'lard=eos_downloader.cli.cli:cli',
        ]
    },
    install_requires=required,
    url="https://github.com/titom73/arista-downloader",
    license="APACHE",
    author="{}".format(eos_downloader.__author__),
    author_email="{}".format(eos_downloader.__email__),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Software Distribution',
        'Topic :: Terminals',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
