#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

__VERSION__ = '0.0.8'

assert sys.version_info[0] == 3, "BitShares-PriceFeed requires Python > 3"

setup(
    name='bitshares-pricefeed',
    version=__VERSION__,
    description='Command line tool to assist with price feed generation',
    long_description=open('README.md').read(),
    download_url='https://github.com/xeroc/bitshares-pricefeed/tarball/' + __VERSION__,
    author='Fabian Schuh',
    author_email='Fabian@chainsquad.com',
    maintainer='Fabian Schuh',
    maintainer_email='Fabian@chainsquad.com',
    url='http://www.github.com/xeroc/bitshares-pricefeed',
    keywords=['bitshares', 'price', 'feed', 'cli'],
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    entry_points={
        'console_scripts': [
            'bitshares-pricefeed = bitshares_pricefeed.cli:main'
        ],
    },
    install_requires=[
        "bitshares>=0.1.8",
        "uptick",
        "prettytable",
        "click",
        "colorama",
        "tqdm",
        "pyyaml",
        "bitcoinaverage",
        "quandl"
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
