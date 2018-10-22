#  ___________________________________________________________________________
#
#  bayota: Bay Optimization Tools for Analysis
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
        os.system('rm -vrf ./build ./dist ./*.egg-info '
                  './*.col ./*nl ./*.row ./*.sol ./logfile_loadobjective.log')

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(setuptools.command.test.test):

    def run_tests(self):
        """Customized run"""
        # deferred import, because outside the eggs aren't loaded
        print('no tests specified at the top(bayota package)-level)')
        pass
        # import shlex
        # import pytest
        #
        # this_project_dir = os.path.dirname(os.path.abspath(__file__))
        #
        # pytest_args = '%s' % os.path.join(this_project_dir, 'src') +\
        #               ' --rootdir=%s' % this_project_dir +\
        #               ' --cov=%s' % os.path.join(this_project_dir, 'src') +\
        #               ' --cov-report=term-missing' +\
        #               ' --cov-report=html:%s' % os.path.join(this_project_dir, 'htmlcov')
        #
        # print('pytest args :\n %s' % pytest_args)
        # errno = pytest.main(shlex.split(pytest_args, posix="win" not in sys.platform))
        # sys.exit(errno)


with open('README.md') as f:
    readme_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()

install_requires = ['pytest',
                    'amplpy',
                    'pandas',
                    'pyomo'
                    ]

setup(name='bayota',
      version='0.0.1',
      description='Python package of optimization tools for the Chesapeake Bay Program',
      long_description=readme_text,
      author='Daniel Kaufman',
      author_email='dkaufman@chesapeakebay.net',
      url='https://gitlab.com/daka42',
      license=license_text,
      packages=find_packages(),  #['src', 'scripts', 'castjeeves', 'castjeeves.CastJeeves'],
      include_package_data=True,
      install_requires=install_requires,
      # test_suite="src.tests",
      setup_requires=['pytest-runner'],
      tests_require=['pytest',
                     'pytest-cov'],
      cmdclass={'clean': CleanCommand,
                'test': TestCommand}
      )
