import pandas as pd


class OptInstance:
    def __init__(self):
        """Represent the options and subset of data necessary for conducting a particular optimization run
        """

        self.name = None
        self.description = None
        self.baseyear = None
        self.basecondname = None
        self.wastewatername = None
        self.costprofilename = None
        self.geoscalename = None
        self.geoareanames = None

        self.geographies_included = None
        # an LRSeg list for this instance (w/accompanying county, stateabbrev, in/out CBWS,
        #                                  major/minor/state basin, river

        self.agencies_included = None
        # list of agencies selected to specify free parameter groups

        self.sectors_included = None
        # list of sectors selected to specify free parameter groups

    def load_from_csv(self, optionsfile):
        pass

    def save_metadata(self, metadata_results):
        print('metadata in optinstance saving:')
        print(metadata_results)

        self.name = metadata_results.name
        self.description = metadata_results.description
        self.baseyear = metadata_results.baseyear
        self.basecondname = metadata_results.basecond
        self.wastewatername = metadata_results.wastewater
        self.costprofilename = metadata_results.costprofile
        self.geoscalename = metadata_results.scale
        self.geoareanames = metadata_results.area

        #self.get_geographies_included(areanames=self.geoareanames)

    def set_geography(self, geotable=None):
        self.geographies_included = geotable
