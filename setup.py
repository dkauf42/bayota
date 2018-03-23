# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.md') as f:
    readme_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()

install_requires = ['numpy==1.14.2',
                    'pandas==0.22.0',
                    'Pmw==2.0.1',
                    'pytz==2018.3',
                    'six==1.11.0',
                    'tqdm==4.19.8',
                    'xlrd==1.1.0',
                    'pyodbc==4.0.17'
                    ]

setup(name='OptSandbox',
      version='0.1.0',
      description='Python package to create CAST scenarios for cost optimization',
      long_description=readme_text,
      author='Daniel Kaufman',
      author_email='dkaufman@chesapeakebay.net',
      url='https://gitlab.com/daka42',
      license=license_text,
      packages=['sandbox', 'data', 'temp', 'output'],
      include_package_data=True,
      install_requires=install_requires,
      test_suite="sandbox.tests"
      )
