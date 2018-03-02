#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""
import sys
import os
import timeit

from util.ScenarioRandomizer import ScenarioRandomizer
from util.InputsToCast import InputsToCast
from util.OptInstance import OptInstance

import tkinter as tk
from gui.toplevelframes.mainwindow import MainWindow

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main():
    start_time = timeit.default_timer()
    runner()  # An optimization instance runner is called, and possibility matrices are generated.
    print("Loading time", timeit.default_timer() - start_time)
    print('<DONE>')


def runner(numinstances=1):
    """generate an OptInstance that populates with metadata, freeparamgroups, constraints, and a possibility matrix
    Parameters:
    Note:
        This function manages the sequence of events from user-input to initial scenario generation
    """
    for i in range(numinstances):
        # Load the Source Data and Base Condition tables
        oinstance = OptInstance()
        oinstance.load_tables()

        # """ Start the GUI """
        root = tk.Tk()  # Create a tkinter window for the mainwindow
        with MainWindow(root, optinstance=oinstance) as mainwindow:
            mainwindow.pack(side="top", fill="both", expand=True)
            root.title("Optimization Options")
        root.mainloop()
        if not hasattr(root, 'results'):
            raise ValueError('No options specified.')
        else:
            print(root.results)
        # raise ValueError('Runner: temp halt')
        # """""""""""""""""""""
        print(oinstance)
        # Generate a matrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        oinstance.generate_possibilitymatrix()
        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        print('>> Generating random integers for each (Geo, Agency, Source, BMP) coordinate')
        ScenarioRandomizer(oinstance.possibility_matrix.ndas)
        ScenarioRandomizer(oinstance.possibility_matrix.anim)
        ScenarioRandomizer(oinstance.possibility_matrix.manu)
        oinstance.possibility_matrix.ndas.to_csv('./output/testwrite_Scenario_possmatrix_ndas.csv')  # write possibilities matrix to file
        oinstance.possibility_matrix.anim.to_csv('./output/testwrite_Scenario_possmatrix_anim.csv')  # write possibilities matrix to file
        oinstance.possibility_matrix.manu.to_csv('./output/testwrite_Scenario_possmatrix_manu.csv')  # write possibilities matrix to file
        inputobj = InputsToCast(oinstance.possibility_matrix, optinstance=oinstance)
        inputobj.matrix_to_table()
        print('<Runner Loading Complete>')


if __name__ == '__main__':
    main()
