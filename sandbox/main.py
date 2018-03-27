#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""
import sys
import os
import timeit
import tkinter as tk

from sandbox.gui.toplevelframes.mainwindow import MainWindow
from sandbox.util.InputsToCast import InputsToCast
from sandbox.util.OptInstance import OptInstance

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main(no_gui=False):
    start_time = timeit.default_timer()
    runner(no_gui=no_gui)  # An optimization instance runner is called, and possibility matrices are generated.
    print("Loading time", timeit.default_timer() - start_time)
    print('<DONE>')


def runner(numinstances=1, no_gui=False):
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
        if no_gui is True:
            print('We know there is no Display, trying without...')
            root = tk.Tcl()
        else:
            root = tk.Tk()  # Create a tkinter window
        mainwindow = MainWindow(root, optinstance=oinstance, no_gui=no_gui)
        mainwindow.pack(side="top", fill="both", expand=True)
        root.title("Optimization Options")
        root.mainloop()
        print(oinstance)

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        oinstance.scenario_randomizer()

        inputobj = InputsToCast(oinstance.pmatrices, optinstance=oinstance)
        inputobj.matrix_to_table()
        print('<Runner Loading Complete>')


if __name__ == '__main__':
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    import argparse

    parser = argparse.ArgumentParser(description='Create an Optimization Instance')
    parser.add_argument('--nogui', action='store_true')
    args = parser.parse_args()

    main(no_gui=args.nogui)
