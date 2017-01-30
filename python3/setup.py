'''
This script provides the necessary logic for building a distribution file of our
helpers for the lsing2172 inginious tasks.

Author: X. Gillard
Date  : Jan. 27, 2017
'''

import os
from setuptools import setup

setup(
    name         = "lsinf2172-inginious-utils",
    version      = "1.0rc7",
    author       = "X. Gillard",
    author_email = "xavier.gillard [at] uclouvain.be",
    description  = "Helper classes to ease the writing of tests on inginious",
    license      = "Apache",
    packages     = ['lsinf2172'],
    package_data = {'lsinf2172': [
                        'resources/Rel-standalone/*.txt',
                        'resources/Rel-standalone/*.jar'
                    ]
    },
    classifiers  = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
)