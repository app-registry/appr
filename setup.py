#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()


requirements = [
    'futures',
    'redis',
    'python-etcd',
    'semantic_version',
    'peewee',
    'flask',
    'Flask>=0.10.1',
    'flask-cors',
]


test_requirements = [
    "pytest",
    "pytest-cov",
    'pytest-flask',
    'pytest-sugar',
    "pytest-ordering",
    "requests-mock"
]


setup(
    name='cnr-server',
    version='0.2.5',
    description="cloud-native app registry server",
    long_description=readme,
    author="Antoine Legrand",
    author_email='2t.antoine@gmail.com',
    url='https://github.com/ant31/cn-app-registry/cnr-server',
    packages=[
        'cnr',
        'cnr.tests',
        'cnr.api',
        'cnr.api.impl',
        'cnr.models',
        'cnr.models.kv',
        'cnr.models.kv.etcd',
        'cnr.models.kv.redis',
        'cnr.models.kv.filesystem',
    ],
    package_dir={'cnr':
                 'cnr'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache License version 2",
    zip_safe=False,
    keywords=['cnr', 'cnrpy', 'kubernetes'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    setup_requries=['pytest-runner'],
    tests_require=test_requirements,
    dependency_links=[
        'https://github.com/jplana/python-etcd/archive/0d0145f5e835aa032c97a0a5e09c4c68b7a03f66.zip#egg=python-etcd'
    ]

)
