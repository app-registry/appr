#!/usr/bin/env python
# -*- coding: utf-8 -*-


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

cli_requirements = [
    'tabulate',
    'termcolor'
    ]

test_requirements = [
    "pytest",
    "coverage",
    "pytest-cov",
    "pytest-ordering",
    "requests-mock"
]

requirements = base_requirements + cli_requirements

setup(
    name='cnrclient',
    version='0.3.1',
    description="cloud-native app registry server",
    long_description=readme,
    author="Antoine Legrand",
    author_email='2t.antoine@gmail.com',
    url='https://github.com/ant31/cn-app-registry/cnrclient-server',
    packages=[
        'cnrclient',
        'cnrclient.commands',
        'cnrclient.formats',
        'cnrclient.formats.helm',
        'cnrclient.formats.kpm',
    ],
    scripts=[
        'bin/cnr'
    ],
    package_dir={'cnrclient':
                 'cnrclient'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache License version 2",
    zip_safe=False,
    keywords=['cnrclient', 'cnrclientpy', 'kubernetes'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
