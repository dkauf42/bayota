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
from sandbox.util.InputsToCast import InputsToCast
from sandbox.util.OptCase import OptCase

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main(numinstances=1, testcase=None):
    """Generate an OptCase that populates with metadata, freeparamgroups, constraints, and a parametermatrix
    Parameters:
    Note:
        This function manages the sequence of events from user-input to initial scenario generation
    """
    start_time = timeit.default_timer()
    for i in range(numinstances):
        # Load the Source Data and Base Condition tables
        optcase = OptCase()
        optcase.load_tables()

        if testcase == 1:
            # No gui, and just Anne Arundel county.
            # TODO: make this work without a gui....
            # TODO: Then make it work with the sqltables!
            # TODO: fix the list of source data tables in the SourceData.py file
            """For Testing Purposes"""
            optcase.name = 'TestOne'
            optcase.description = 'TestOneDescription'
            optcase.baseyear = '1995'
            optcase.basecondname = 'Example_BaseCond2'
            optcase.wastewatername = 'Example_WW1'
            optcase.costprofilename = 'Example_CostProfile1'
            optcase.geoscalename = 'County'
            optcase.geoareanames = ['Adams, PA']

            optcase.populate_geography_from_scale_and_areas()
            optcase.agencies_included = optcase.queries.base. \
                get_agencies_in_lrsegs(lrsegs=optcase.geography.LandRiverSegment)
            optcase.sectors_included = optcase.queries.source.get_all_sector_names()

            # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
            optcase.generate_emptyparametermatrices()
            optcase.mark_eligibility()
            optcase.generate_boundsmatrices()
            pass
        else:
            # Run the GUI
            root = tk.Tk()  # Create a tkinter window
            mainwindow = MainWindow(root, optcase=optcase)
            mainwindow.pack(side="top", fill="both", expand=True)
            root.title("Optimization Options")
            root.mainloop()
            print(optcase)

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        optcase.scenario_randomizer()

        inputobj = InputsToCast(optcase.pmatrices, optcase=optcase)
        inputobj.matrix_to_table()
        print('<Runner Loading Complete>')
        print("Loading time", timeit.default_timer() - start_time)
        print('<DONE>')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='SANDBOXER',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                                 Please do not mess up this text!
                                                 Create and run an optimization case
                                                 --------------------------------
                                                     I have indented it
                                                     exactly the way
                                                     I want it
                                                 '''))
    parser.add_argument('-t', choices=[1, 2, 3], type=int, help='test case #')
    args = parser.parse_args()

    main(testcase=args.t)
