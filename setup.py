# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

#with open('LICENSE') as f:
#    license = f.read()

setup(
    name='OptSandbox',
    version='0.1.0',
    description='Python package to create CAST scenarios for cost optimization',
    long_description=readme,
    author='Daniel Kaufman',
    author_email='dkaufman@chesapeakebay.net',
    url='https://gitlab.com/daka42',
    license=license,
    packages=find_packages(exclude=('docs', 'documentation_ppts',
                                    'sphinx_doc', 'sphinx_guides', 'test')),
    install_requires=['numpy', 'pandas', 'Pmw', 'python-dateutil', 'pytz',
                      'six', 'tqdm', 'xlrd']
)
