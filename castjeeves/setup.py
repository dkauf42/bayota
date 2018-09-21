#  ___________________________________________________________________________
#
#  castjeeves: Utility package for querying csv formatted CAST source data.
#  Developed under a grant awarded to the Chesapeake Research Consortium, Inc.
#  and work occurring at U.S. EPA Chesapeake Bay Program Office, Annapolis, MD
#  ___________________________________________________________________________
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, Command, find_packages
import setuptools.command.test


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


class TestCommand(setuptools.command.test.test):

    def run_tests(self):
        """Customized run"""
        # deferred import, because outside the eggs aren't loaded
        import shlex
        import pytest

        this_project_dir = os.path.dirname(os.path.abspath(__file__))

        pytest_args = '--rootdir=%s' % this_project_dir +\
                      ' --cov=%s' % os.path.join(this_project_dir, 'src') +\
                      ' --cov-report=term-missing' +\
                      ' --cov-report=html:%s' % os.path.join(this_project_dir, 'htmlcov') +\
                      ' %s' % os.path.join(this_project_dir, 'src/tests')
        #  other tests here...
        print('pytest args :\n %s' % pytest_args)
        errno = pytest.main(shlex.split(pytest_args))
        sys.exit(errno)


with open('README.md') as f:
    readme_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()

install_requires = ['numpy>=1.14.2',
                    'pandas==0.22.0',  # there is currently an issue with pandas==0.23.0
                    'pytest'
                    ]

setup(name='castjeeves',
      version='0.0.2',
      description='Python package to query csv formatted CAST source data',
      long_description=readme_text,
      author='Daniel Kaufman',
      author_email='dkaufman@chesapeakebay.net',
      url='https://gitlab.com/daka42',
      license=license_text,
      packages=find_packages(),
      include_package_data=True,
      install_requires=install_requires,
      # test_suite="src.tests",
      setup_requires=['pytest-runner'],
      tests_require=['pytest',
                     'pytest-cov'],
      cmdclass={'clean': CleanCommand,
                'test': TestCommand}
      )
