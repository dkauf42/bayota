import os
import pickle
import pandas as pd

from util.SourceData import SourceData
from util.BaseCondition import BaseCondition
from util.county import County
from util.state import State


class Scenario:
    def __init__(self, optionsfile="../options_AAcounty.txt"):
        """A wrapper to generate and hold multiple Geo objects

        :param optionsfile:
        """
        self.srcdataobj = None
        self.baseconditionobj = None
        self.geoobjs = []

        # An options file (specifying the geographic regions, agencies, etc.) is loaded for this scenario.
        #BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin, OutOfCBWS, AgencyCode
        self.options = None
        self.option_headers = None
        self.optionsload(optionsfile=optionsfile)

        # Load the Source Data and Base Condition tables
        self.tblload()

        # turn options into a BaseCondition query
        self.baseconquery()

    def optionsload(self, optionsfile):
        """Loads an 'options' file that represents the user choices for a particular scenario

        Parameters
        ----------
        optionsfile : `str`
            file path of the 'options' csv file for the user scenario

        Notesasdasd
        -----
        The options file should have the following columns:
            - BaseCondition,LandRiverSegment,CountyName,StateAbbreviation,StateBasin,OutOfCBWS,AgencyCode
        Any blank options should be specified by a '-'

        """
        self.options = pd.read_table(optionsfile, sep=',', header=0)
        self.option_headers = list(self.options.columns.values)

    def tblload(self):
        # Objects that contain the BMP Source Data and Base Condition Data are loaded or generated.
        picklename = 'cast_opt_src.obj'  # BMP Source Data from the Excel Spreadsheet
        if os.path.exists(picklename):
            with open(picklename, 'rb') as f:
                self.srcdataobj = pickle.load(f)
        else:
            self.srcdataobj = SourceData()  # generate source data object if none exists
            with open(picklename, 'wb') as f:
                pickle.dump(self.srcdataobj, f)
        picklename = 'cast_opt_base.obj'  # Base Condition Data (which has Load Source acreage per LRS)
        if os.path.exists(picklename):
            with open(picklename, 'rb') as f:
                self.baseconditionobj = pickle.load(f)
        else:
            self.baseconditionobj = BaseCondition()  # generate base condition object if none exists
            with open(picklename, 'wb') as f:
                pickle.dump(self.baseconditionobj, f)
        print('<Loaded> BMP Source Data and Base Condition Data.')

    def baseconquery(self):

        self.options
        self.option_headers

        self.baseconditionobj


        # A list is generated containing a Geo for each state and county.
        if 'states' in self.option_headers:
            for x in self.options.states:
                g = State(name=x, srcdata=self.srcdataobj, baseconditiondata=self.baseconditionobj)
                self.geoobjs.append(g)
        if 'counties' in self.option_headers:
            for x in self.options.counties:
                g = County(name=x, srcdata=self.srcdataobj, baseconditiondata=self.baseconditionobj)
                self.geoobjs.append(g)
        print('<Loaded> Geo-objects: ')
