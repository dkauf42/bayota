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


def main(numinstances=1, testcase=None, scale='', areanames=None):
    """Generate an OptCase that populates with metadata, freeparamgroups, constraints, and a parametermatrix
    Parameters:
        numinstances (int):
        testcase (int):
        scale (str): specified for a custom scenario
        areanames (list of str): specified for a custom scenario
    Note:
        This function manages the sequence of events from user-input to initial scenario generation
    """
    start_time = timeit.default_timer()
    for i in range(numinstances):
        # Load the Source Data and Base Condition tables
        if testcase == 1:
            print('\nTEST CASE 1 : No GUI; Only "Adams, PA" County\n')
            oc = OptCase.loadexample(name='adamscounty')

        elif testcase == 2:
            print('\nTEST CASE 2 : No GUI; 2 Counties: ("Adams, PA" and "Anne Arundel, MD")\n')
            oc = OptCase.loadexample(name='adams_and_annearundel')

        elif testcase == 3:
            print('\nTEST CASE 3 : No GUI; 3 Counties: ("Adams, PA", "York, PA", and "Anne Arundel, MD")\n')
            oc = OptCase.loadexample(name='adams_annearundel_and_york')

        elif testcase == 99:
            print('\nTEST CASE 99 : No GUI; Custom geography specified.\n')
            print('\tScale = %s\n' % scale)
            print('\tAreanames = %s\n' % areanames)
            oc = OptCase.loadcustom(scale=scale, areanames=areanames)

        elif not testcase:
            oc = OptCase()
            # Run the GUI
            root = tk.Tk()  # Create a tkinter window
            mainwindow = MainWindow(root, optcase=oc)
            mainwindow.pack(side="top", fill="both", expand=True)
            root.title("Optimization Options")
            root.mainloop()
        else:
            raise ValueError('Unexpected test case argument')

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        # optcase.generate_single_scenario(scenariotype='random')
        print(oc)
        oc.generate_multiple_scenarios(scenariotype='hypercube')

        # Write scenario tables to file.

        print('<Runner Loading Complete>')
        print("Loading time", timeit.default_timer() - start_time)
        print('<DONE>')

        oc.successful_creation_log = True

        return oc


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='SANDBOXER',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                                 Create and run an optimization case
                                                 --------------------------------
                                                 1. Generate a Decision Space    
                                                      * specify metadata
                                                         - base condition
                                                         - wastewatername data
                                                         - cost profile
                                                         - geography
                                                      * specify free parameter groups
                                                      * specify constraints
                                                 2. Generate a Scenario
                                                 '''))
    parser.add_argument('-t', choices=[1, 2, 3, 99], type=int, help='test case #')
    parser.add_argument('-s', '--scale',
                        action="store", type=str, dest="s",
                        help="geographic scale string", default="")
    parser.add_argument('-a', '--areanames', nargs='+',
                        action="store", type=str, dest="a",
                        help="geographic area names", default="")
    args = parser.parse_args()

    main(testcase=args.t, scale=args.s, areanames=args.a)
