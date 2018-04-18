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

from sandbox.gui.toplevelframes.mainwindow import MainWindow
from sandbox.util.OptCase import OptCase

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main(numinstances=1, testcase=None):
    """Generate an OptCase that populates with metadata, freeparamgroups, constraints, and a parametermatrix
    Parameters:
        numinstances (int):
        testcase (int):
    Note:
        This function manages the sequence of events from user-input to initial scenario generation
    """
    start_time = timeit.default_timer()
    for i in range(numinstances):
        # Load the Source Data and Base Condition tables
        optcase = OptCase()
        optcase.load_tables()

        if testcase == 1:
            print('\nTEST CASE 1 : No GUI; Only "Adams, PA" County\n')
            optcase.load_example(name='adamscounty')
            optcase.proceed_from_geography_to_decision_space()

        elif testcase == 2:
            print('\nTEST CASE 2 : No GUI; 2 Counties: ("Adams, PA" and "Anne Arundel, MD")\n')
            optcase.load_example(name='adams_and_annearundel')
            optcase.proceed_from_geography_to_decision_space()

        elif testcase == 3:
            print('\nTEST CASE 3 : No GUI; 3 Counties: ("Adams, PA", "York, PA", and "Anne Arundel, MD")\n')
            optcase.load_example(name='adams_annearundel_and_york')
            optcase.proceed_from_geography_to_decision_space()

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
        scenario = optcase.generate_scenario(scenariotype='random')

        # Write scenario tables to file.
        #inputobj = InputsToCast(optcase.pmatrices, optcase=optcase)
        #inputobj.matrix_to_table()
        print('<Runner Loading Complete>')
        print("Loading time", timeit.default_timer() - start_time)
        print('<DONE>')

        return 1


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
