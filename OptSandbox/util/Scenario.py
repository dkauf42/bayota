from util.TblLoader import TblLoader
from util.PossibilitiesMatrix import PossibilitiesMatrix
from util.ScenarioRandomizer import ScenarioRandomizer
from util.InputsToCast import InputsToCast
from util.OptInstance import OptInstance
from tables.TblQuery import TblQuery

import tkinter as tk
from gui.toplevelframes.mainwindow import MainWindow


class Scenario:
    def __init__(self, optionsfile=''):
        """A wrapper to generate and hold the metadata for a scenario

        Parameters:
            optionsfile (str)

        Note:
            This class manages the sequence of events from user-input to
            initial scenario generation

        """
        # Load the Source Data and Base Condition tables
        tablesobj = TblLoader()
        tblqry = TblQuery(tables=tablesobj)
        oinstance = OptInstance(queries=tblqry)

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
        #raise ValueError('Scenario: temp halt')
        #"""

        print(oinstance)

        # Generate a matrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.possmatrix = PossibilitiesMatrix(tables=tablesobj, optinstance=oinstance)

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        print('>> Generating random integers for each (Geo, Agency, Source, BMP) coordinate')
        ScenarioRandomizer(self.possmatrix.ndas)
        ScenarioRandomizer(self.possmatrix.anim)
        ScenarioRandomizer(self.possmatrix.manu)

        self.possmatrix.ndas.to_csv('./output/testwrite_Scenario_possmatrix_ndas.csv')  # write possibilities matrix to file
        self.possmatrix.anim.to_csv('./output/testwrite_Scenario_possmatrix_anim.csv')  # write possibilities matrix to file
        self.possmatrix.manu.to_csv('./output/testwrite_Scenario_possmatrix_manu.csv')  # write possibilities matrix to file

        inputobj = InputsToCast(self.possmatrix, tables=tablesobj)
        inputobj.matrix_to_table()

        print('<Scenario Loading Complete>')

    def run_gui(self, optinstance=None):
        with MainWindow(self.root, optinstance=optinstance) as mainwindow:
            mainwindow.pack(side="top", fill="both", expand=True)
            self.root.title("Optimization Options")

    def clean_up(self):
        print('Sequencer.clean_up: first line')
