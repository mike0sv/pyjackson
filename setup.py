#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


long_description = '%s\n%s' % (re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
                               re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst')))

setup(
    name='pyjackson',
    version='0.0.25',
    license='Apache-2.0',
    description='PyJackson is a serialization library based on type hinting ',
    long_description=long_description,
    author='Mikhail Sveshnikov',
    author_email='mike0sv@gmail.com',
    url='https://github.com/mike0sv/pyjackson',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://pyjackson.readthedocs.io/',
        'Changelog': 'https://pyjackson.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/mike0sv/pyjackson/issues',
    },
    keywords=[
        'pyjackson', 'jackson', 'serialization'
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.6',
    install_requires=[
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    setup_requires=[
        'pytest-runner',
    ],
)
