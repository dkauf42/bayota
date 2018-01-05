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
        options = configobj.options
        option_headers = configobj.option_headers

        # Objects that contain the BMP Source Data and Base Condition Data are loaded or generated.
        picklename = 'cast_opt_src.obj'  # BMP Source Data from the Excel Spreadsheet
        if os.path.exists(picklename):
            with open(picklename, 'rb') as f:
                srcdata = pickle.load(f)
        else:
            srcdata = SrcDataObj()  # generate source data object if none exists
            with open(picklename, 'wb') as f:
                pickle.dump(srcdata, f)
        picklename = 'cast_opt_base.obj'  # Base Condition Data (which has Load Source acreage per LRS)
        if os.path.exists(picklename):
            with open(picklename, 'rb') as f:
                base_condition = pickle.load(f)
        else:
            base_condition = BaseCondObj()  # generate base condition object if none exists
            with open(picklename, 'wb') as f:
                pickle.dump(base_condition, f)
        print('<Loaded> BMP Source Data and Base Condition Data.')

        # A list is generated containing a Geo for each state and county.
        self.geoobjs = []
        if 'states' in option_headers:
            for x in options.states:
                g = State(name=x, srcdata=srcdata, baseconditiondata=base_condition)
                self.geoobjs.append(g)
        if 'counties' in option_headers:
            for x in options.counties:
                g = County(name=x, srcdata=srcdata, baseconditiondata=base_condition)
                self.geoobjs.append(g)
        print('<Loaded> Geo-objects: ')
