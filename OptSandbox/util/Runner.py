from util.ScenarioRandomizer import ScenarioRandomizer
from util.InputsToCast import InputsToCast
from util.OptInstance import OptInstance

import tkinter as tk
from gui.toplevelframes.mainwindow import MainWindow


class Runner:
    def __init__(self, optionsfile=''):
        """A wrapper to generate and hold the metadata for a scenario

        Parameters:
            optionsfile (str)

        Note:
            This class manages the sequence of events from user-input to
            initial scenario generation

        """
        # Load the Source Data and Base Condition tables
        oinstance = OptInstance()
        oinstance.load_tables()

        """ TO RUN WITH A GUI """
        #"""
        # Create a tkinter window for the mainwindow
        self.root = tk.Tk()
        # Start the GUI
        self.run_gui(optinstance=oinstance)
        self.root.mainloop()
        if not hasattr(self.root, 'results'):
            raise ValueError('No options specified.')
        else:
            print(self.root.results)
        #raise ValueError('Runner: temp halt')
        #"""

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

    def run_gui(self, optinstance=None):
        with MainWindow(self.root, optinstance=optinstance) as mainwindow:
            mainwindow.pack(side="top", fill="both", expand=True)
            self.root.title("Optimization Options")
