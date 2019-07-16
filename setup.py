# -*- coding: utf-8 -*-
"""
BayOTA: Bay Optimization Tools for Analysis
Developed under a grant awarded to the Chesapeake Research Consortium, Inc.
and work occurring at U.S. EPA Chesapeake Bay Program Office, Annapolis, MD

"""

import os
import sys
from setuptools import setup, Command, find_packages
import setuptools.command.test
import setuptools.command.develop
import setuptools.command.install


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    @staticmethod
    def run():
        os.system('rm -vrf ./build ./dist ./*.egg-info '
                  './*.col ./*nl ./*.row ./*.sol ./logfile_loadobjective.log ./slurm_*.out ./slurm_*.err')

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(setuptools.command.test.test):

    def run_tests(self):
        """Customized run"""
        # deferred import, because outside the eggs aren't loaded
        print('no tests specified at the top(bayota package)-level')
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


class PostDevelopCommand(setuptools.command.develop.develop):
    """Post-installation for development mode."""
    def run(self):
        setuptools.command.develop.develop.run(self)


class PostInstallCommand(setuptools.command.install.install):
    """Post-installation for installation mode."""
    def run(self):

        from bayota_settings.base import create_workspace_directory_and_set_up_user_config_files

        create_workspace_directory_and_set_up_user_config_files()

        setuptools.command.install.install.run(self)


with open('README.md', encoding='utf-8') as f:
    readme_text = f.read()

with open('VERSION') as version_file:
    version = version_file.read().strip()

with open('LICENSE') as f:
    license_text = f.read()

install_requires = ['pyomo',
                    'cloudpickle',
                    'pyyaml',
                    'numpy',
                    'pandas',
                    'matplotlib',
                    'pytest',
                    'boto3',  # necessary for moving files in aws s3
                    'requests'  # necessary for moving files in aws s3
                    #'pyutilib'
                    ]
# boto3 and requests are also required IF using AWS and you want to move files to s3

setup(name='bayota',
      version=version,
      description='Python package of optimization tools for the Chesapeake Bay Program',
      long_description=readme_text,
      author='Daniel Kaufman',
      author_email='dkaufman@chesapeakebay.net',
      url='https://gitlab.com/daka42',
      license=license_text,
      packages=find_packages(),  #['castjeeves', 'bayom_e', 'sandbox', 'util'],
      include_package_data=True,
      install_requires=install_requires,
      setup_requires=['pytest-runner'],
      tests_require=['pytest',
                     'pytest-cov'],
      cmdclass={'clean': CleanCommand,
                'test': TestCommand,
                'develop': PostDevelopCommand,
                'install': PostInstallCommand},
      entry_points={"console_scripts":
                    ['bayota = bin.bayota_efficiency:main']}
      )
