#!/usr/bin/env python
# -*- coding: utf-8 -*-
# yapf:disable
from __future__ import absolute_import, division, print_function

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

base_requirements = [
    'future',
    'futures',
    'requests',
]

server_requirements = [
    'redis',
    'python-etcd',
    'semantic_version',
    'flask',
    'Flask>=0.10.1',
    'flask-cors',
    'gunicorn>=19.7',
    "gevent",
]

cli_requirements = [
    'tabulate',
    'termcolor',
    'pyyaml',
]

extra_requirements = [
    'urllib3[secure]',
    'jsonnet',
    'jinja2>=2.8',
    'jsonpatch',
    'tabulate',
    'ecdsa',
    'cryptography',
    ]

test_requirements = [
    "pytest",
    "coverage",
    "pytest-cov",
    "pytest-ordering",
    "requests-mock"
    "coverage>=4.0",
    "flake8",
    "pytest-flask>=0.10.0",
    "tox>=2.1.1",
    "sphinxcontrib-napoleon",
    "gunicorn>=0.19",
]

requirements = base_requirements + cli_requirements + server_requirements + extra_requirements


setup(
    name='appr',
    version='0.7.0-pre',
    description="cloud-native app registry server",
    long_description=readme,
    author="Antoine Legrand",
    author_email='2t.antoine@gmail.com',
    url='https://github.com/app-registry/appr-server',
    packages=[
        'appr',
        'appr.commands',
        'appr.plugins',
        'appr.formats',
        'appr.formats.helm',
        'appr.formats.appr',
        'appr.tests',
        'appr.api',
        'appr.api.impl',
        'appr.models',
        'appr.models.kv',
        'appr.models.kv.etcd',
        'appr.models.kv.redis',
        'appr.models.kv.filesystem',
    ],
    scripts=['bin/appr'],
    package_dir={'appr': 'appr'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache License version 2",
    zip_safe=False,
    keywords=['apprclient', 'apprclientpy', 'kubernetes'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    setup_requires=['pytest-runner'],
    test_suite='tests',
    tests_require=test_requirements,)
