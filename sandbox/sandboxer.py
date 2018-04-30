#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""
import os
import sys
import timeit
import argparse
import textwrap
import tkinter as tk

from sandbox.util.OptCase import OptCase
from sandbox.gui.toplevelframes.MainWindow import MainWindow

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main(numinstances=1, testcase=None, scale='', areanames=''):
    """Generate an OptCase that populates with metadata, freeparamgroups, constraints, and a parametermatrix
    Parameters:
        numinstances (int):
        testcase (int):
        scale (str): specified for a custom scenario
        areanames (str): specified for a custom scenario
    Note:
        This function manages the sequence of events from user-input to initial scenario generation
    """
    start_time = timeit.default_timer()
    for i in range(numinstances):
        # Load the Source Data and Base Condition tables
        optcase = OptCase()

        if testcase == 1:
            print('\nTEST CASE 1 : No GUI; Only "Adams, PA" County\n')
            optcase.load_example(name='adamscounty')
            optcase.generate_decisionspace_using_case_geography()

        elif testcase == 2:
            print('\nTEST CASE 2 : No GUI; 2 Counties: ("Adams, PA" and "Anne Arundel, MD")\n')
            optcase.load_example(name='adams_and_annearundel')
            optcase.generate_decisionspace_using_case_geography()

        elif testcase == 3:
            print('\nTEST CASE 3 : No GUI; 3 Counties: ("Adams, PA", "York, PA", and "Anne Arundel, MD")\n')
            optcase.load_example(name='adams_annearundel_and_york')
            optcase.generate_decisionspace_using_case_geography()

        elif testcase == 99:
            print('\nTEST CASE 99 : No GUI; Custom geography specified.\n')
            optcase.custom_scenario(scale=scale, areanames=areanames)
            optcase.generate_decisionspace_using_case_geography()

        elif not testcase:
            # Run the GUI
            root = tk.Tk()  # Create a tkinter window
            mainwindow = MainWindow(root, optcase=optcase)
            mainwindow.pack(side="top", fill="both", expand=True)
            root.title("Optimization Options")
            root.mainloop()
            print(optcase)
        else:
            raise ValueError('Unexpected test case argument')

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        optcase.generate_single_scenario(scenariotype='random')
        # optcase.generate_multiple_scenarios(scenariotype='hypercube')
        #
        # Write scenario tables to file.

        print('<Runner Loading Complete>')
        print("Loading time", timeit.default_timer() - start_time)
        print('<DONE>')

        optcase.successful_creation_log = True

        return optcase


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='SANDBOXER',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                                 Create and run an optimization case
                                                 --------------------------------
                                                 1. Generate a Decision Space    
                                                      * specify metadata
                                                         - base condition
                                                         - wastewater data
                                                         - cost profile
                                                         - geography
                                                      * specify free parameter groups
                                                      * specify constraints
                                                 2. Generate a Scenario
                                                 '''))
    parser.add_argument('-t', choices=[1, 2, 3], type=int, help='test case #')
    args = parser.parse_args()

    main(testcase=args.t)
