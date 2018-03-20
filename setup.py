# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

#with open('LICENSE') as f:
#    license = f.read()

install_requires = ['numpy==1.14.2',
                    'pandas==0.22.0',
                    'Pmw==2.0.1',
                    'python-dateutil==2.7.0',
                    'pytz==2018.3',
                    'six==1.11.0',
                    'tqdm==4.19.8',
                    'xlrd==1.1.0',
                    ]

setup(
    name='OptSandbox',
    version='0.1.0',
    description='Python package to create CAST scenarios for cost optimization',
    long_description=readme,
    author='Daniel Kaufman',
    author_email='dkaufman@chesapeakebay.net',
    url='https://gitlab.com/daka42',
    license=license,
    packages=['sandbox', 'data', 'temp', 'output'],
    include_package_data=True,
    install_requires=install_requires,
    test_suite="tests"
)

#packages = find_packages(exclude=['docs', 'documentation_ppts',
#                                  'sphinx_doc', 'sphinx_guides', 'test'])
