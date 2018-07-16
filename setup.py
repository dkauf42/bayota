# -*- coding: utf-8 -*-

import os
from setuptools import setup, Command, find_packages


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    @staticmethod
    def run():
        os.system('rm -vrf ./build ./dist ./*.egg-info')

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


with open('README.md') as f:
    readme_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()

install_requires = ['numpy>=1.14.2',
                    'pandas==0.22.0',  # there is currently an issue with pandas==0.23.0
                    # 'Pmw>=2.0.1',
                    # 'pytz>=2018.3',
                    # 'six>=1.11.0',
                    'tqdm>=4.19.8',
                    # 'xlrd>=1.1.0',
                    # 'pyDOE>=0.3.8',
                    # 'requests',
                    # 's3fs',
                    # 'dask',
                    # 'boto3'
                    ]

setup(name='CastJeeves',
      version='0.0.1',
      description='Python package to create CAST scenarios for cost optimization',
      long_description=readme_text,
      author='Daniel Kaufman',
      author_email='dkaufman@chesapeakebay.net',
      url='https://gitlab.com/daka42',
      license=license_text,
      packages=find_packages(),
      include_package_data=True,
      install_requires=install_requires,
      test_suite="util.tests",
      cmdclass={'clean': CleanCommand}
      )
