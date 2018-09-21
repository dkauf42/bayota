#  ___________________________________________________________________________
#
#  efficiencysubproblem: NLP for Efficiency BMPs in CAST.
#  Developed under a grant awarded to the Chesapeake Research Consortium, Inc.
#  and work occurring at U.S. EPA Chesapeake Bay Program Office, Annapolis, MD
#  ___________________________________________________________________________
# -*- coding: utf-8 -*-

"""
Script to generate the installer for efficiencysubproblem.
"""

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

install_requires = ['pytest',
                    'amplpy',
                    'pandas',
                    'pyomo'
                    ]

setup(name='efficiencysubproblem',
      version='0.0.1',
      description='Python package to set up and solve an NLP for efficiency BMPs of CAST',
      long_description=readme_text,
      author='Daniel Kaufman',
      author_email='dkaufman@chesapeakebay.net',
      url='https://gitlab.com/daka42',
      license=license_text,
      packages=find_packages(),  #['src', 'jnotebooks', 'castjeeves', 'castjeeves.CastJeeves'],
      include_package_data=True,
      install_requires=install_requires,
      test_suite="src.tests",
      setup_requires=['pytest-runner'],
      tests_require=['pytest',
                     'pytest-cov'],
      cmdclass={'clean': CleanCommand}
      )
