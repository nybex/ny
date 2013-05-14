# -*- coding: utf-8 -*-

from setuptools import setup

import os

def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py')))

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package(dir):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

packages = find_packages(".")

requires = [
    'toml==0.7.0',
    'boto==2.9.2',
    'envoy==0.0.2',
    'pexpect==2.4',
    'docopt==0.6.1',
    'Jinja2==2.6',
    'prettytable==0.7.2',
    'clint==0.3.1',
]

setup(
    name='ny',
    version='0.0.2',
    packages=packages,
    license='MIT',
    entry_points={
        'console_scripts': [
            'ny = ny.cli:ny',
            'ny-deploy   = ny.cli:ny_deploy',
            'ny-vm       = ny.cli:ny_vm',
            'ny-_spinner = ny.cli:__spinner',
        ],
    },
    long_description=open('README.md').read(),
    install_requires=requires
)
