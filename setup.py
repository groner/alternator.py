from setuptools import setup

import sys
import warnings


#if sys.hexversion < 0x30500f0:
if sys.hexversion < 0x30500b3:
    warnings.warn('alternator works with python 3.5')

with open('README.rst') as fh:
    README = fh.read()

setup(
    name='alternator',
    version='0.1.1',
    description='Create asynchronous generators from coroutines',
    long_description=README,
    url='https://github.com/groner/alternator.py/',
    author='Kai Groner',
    author_email='kai@gronr.com',
    license='BSD',
    packages=['alternator'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests.test_alternator',
)
