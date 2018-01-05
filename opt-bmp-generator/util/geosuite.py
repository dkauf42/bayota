import os
import pickle

from util.srcdataobj import SrcDataObj
from util.basecondobj import BaseCondObj
from util.county import County
from util.state import State
from config import ConfigObj


class GeoSuite:
    def __init__(self, optionsfile="../options_AAcounty.txt"):
        """A wrapper to generate and hold multiple Geo objects

        :param optionsfile:
        """

        # A configuration file, which specifies the geographic regions and agencies to examine, is loaded.
        configobj = ConfigObj(optionsfile=optionsfile)
        self.options = configobj.options
        self.option_headers = configobj.option_headers

        self.srcdata = None
        self.base_condition = None
        self.geoobjs = []

        self.tblload()
        self.suiteload()

    def tblload(self):
        # Objects that contain the BMP Source Data and Base Condition Data are loaded or generated.
        picklename = 'cast_opt_src.obj'  # BMP Source Data from the Excel Spreadsheet
        if os.path.exists(picklename):
            with open(picklename, 'rb') as f:
                self.srcdata = pickle.load(f)
        else:
            self.srcdata = SrcDataObj()  # generate source data object if none exists
            with open(picklename, 'wb') as f:
                pickle.dump(self.srcdata, f)
        picklename = 'cast_opt_base.obj'  # Base Condition Data (which has Load Source acreage per LRS)
        if os.path.exists(picklename):
            with open(picklename, 'rb') as f:
                self.base_condition = pickle.load(f)
        else:
            self.base_condition = BaseCondObj()  # generate base condition object if none exists
            with open(picklename, 'wb') as f:
                pickle.dump(self.base_condition, f)
        print('<Loaded> BMP Source Data and Base Condition Data.')

    def suiteload(self):
        # A list is generated containing a Geo for each state and county.
        if 'states' in self.option_headers:
            for x in self.options.states:
                g = State(name=x, srcdata=self.srcdata, baseconditiondata=self.base_condition)
                self.geoobjs.append(g)
        if 'counties' in self.option_headers:
            for x in self.options.counties:
                g = County(name=x, srcdata=self.srcdata, baseconditiondata=self.base_condition)
                self.geoobjs.append(g)
        print('<Loaded> Geo-objects: ')
