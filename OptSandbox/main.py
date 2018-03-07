#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""
import sys
import os
import timeit
import tkinter as tk

from gui.toplevelframes.mainwindow import MainWindow
from util.InputsToCast import InputsToCast
from util.OptInstance import OptInstance

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main():
    start_time = timeit.default_timer()
    runner()  # An optimization instance runner is called, and possibility matrices are generated.
    print("Loading time", timeit.default_timer() - start_time)
    print('<DONE>')


def runner(numinstances=1):
    """Generate an OptInstance that populates with metadata, freeparamgroups, constraints, and a parametermatrix
    Parameters:
    Note:
        This function manages the sequence of events from user-input to initial scenario generation
    """
    for i in range(numinstances):
        # Load the Source Data and Base Condition tables
        oinstance = OptInstance()
        oinstance.load_tables()

        # Run the GUI
        root = tk.Tk()  # Create a tkinter window
        mainwindow = MainWindow(root, optinstance=oinstance)
        mainwindow.pack(side="top", fill="both", expand=True)
        root.title("Optimization Options")
        root.mainloop()
        print(oinstance)

        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        #oinstance.generate_emptyparametermatrices()

        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        #oinstance.mark_eligibility()

        oinstance.generate_boundsmatrices()

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        oinstance.scenario_randomizer()

        inputobj = InputsToCast(oinstance.pmatrices, optinstance=oinstance)
        inputobj.matrix_to_table()
        print('<Runner Loading Complete>')


if __name__ == '__main__':
    main()
