import os
import pickle
import pandas as pd
import numpy as np

from util.SourceData import SourceData
from util.BaseCondition import BaseCondition
from util.OptionLoader import OptionLoader


class Scenario:
    def __init__(self, optionsfile=''):
        """A wrapper to generate and hold the metadata for a scenario

        :param optionsfile:
        """
        # Load the Source Data and Base Condition tables
        self.srcdataobj = None
        self.baseconditionobj = None
        self.tblload()

        # The scenario options (particular geographic region(s), agencies, etc.) are loaded for this scenario.
        self.options = OptionLoader(optionsfile=optionsfile, srcdataobj=self.srcdataobj)

        # Options are used to query the BaseCondition data and filter only Load Sources with the chosen characteristics
        self.chosen_load_sources = None
        self.baseconquery()
        #print(self.chosen_load_sources.head())

        # Get the list of BMPs available on the chosen load sources
        self.geo_seg_source_bmps = None
        self.bmpquery()

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
        # headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
        #           OutOfCBWS, AgencyCode, Sector
        oh = self.options.headers
        booldf = pd.DataFrame()
        for h in oh:
            optionscolumn = self.options.options[h]
            if (optionscolumn[0] == 'all') | optionscolumn.isnull().values.all():
                # exclude this column from the boolean dataframe if we're just going to get all of the values
                pass
            else:
                # generate boolean for each basecondition row, if its value is in this options column
                booldf[h] = self.baseconditionobj.LSacres[h].isin(optionscolumn)

        """
        Note: For the geographic options (LandRiverSegment, CountyName, StateAbbreviation, StateBasin),
              we want to include rows that are logical ORs of these column values
         
              For example, if options include {County: Anne Arundel, State: DE, StateBasin: WV James River Basin},
              then we want to include load sources from all of those places, not just the intersection of them.
              
              Then, we want the logical AND of those geooptions with the other options
                                                                        (BaseCondition, OutOfCBWS, AgencyCode, Sector)
                                                                               
              Then, we want logical AND of those options with the load sources that have non-zero values
        """
        # A logical OR amongst the geographic options is computed.
        geo_options_list = ('LandRiverSegment', 'CountyName', 'StateAbbreviation', 'StateBasin')
        geooptionsbooldf = booldf[booldf.columns[booldf.columns.isin(geo_options_list)]]
        geooptionsbool = geooptionsbooldf.any(axis=1)

        # A logical AND between the geo-options result and the non-geo-options is computed.
        nongeooptionsbooldf = booldf[booldf.columns.difference(geooptionsbooldf.columns)]
        optionsbool = geooptionsbool & nongeooptionsbooldf.all(axis=1)
        print('All load sources for chosen geo+agency+sector region: %d' % np.sum(optionsbool))

        # Only load sources that have non-zero values are included.
        nonzero_ls_bool = self.baseconditionobj.LSacres['PreBMPAcres'] != 0
        print('Load sources for chosen geo+agency+sector region with >0 acres: %d' % np.sum(optionsbool & nonzero_ls_bool))

        self.chosen_load_sources = self.baseconditionobj.LSacres.loc[optionsbool & nonzero_ls_bool, :]

    def bmpquery(self):
        # Get all the BMPs that are possible on the set of Load sources
        #booldf = pd.DataFrame()
        #booldf[h] = self.baseconditionobj.LSacres[h].isin(optionscolumn)
        self.geo_seg_source_bmps = self.chosen_load_sources.copy()


        # Efficiency BMPs
        bmplist = []  # Create a list to store the data
        totalnumbmps = 0
        for index, row in self.chosen_load_sources.iterrows():
            thesebmps = self.srcdataobj.get(sheetabbrev='efficiencyBMPs', getcolumn='BMPShortName',
                                            by='LoadSource', equalto=row.LoadSource)
            thesebmps = thesebmps.str.lower().unique()
            totalnumbmps += thesebmps.size
            bmplist.append(thesebmps)
        self.geo_seg_source_bmps['eligible_efficiency_bmps'] = bmplist
        print('total no. of eligible "efficiency" BMPs: <%d>' % totalnumbmps)

        # Land Conversion BMPs
        bmplist = []
        totalnumbmps = 0
        for index, row in self.chosen_load_sources.iterrows():
            thesebmps = self.srcdataobj.get(sheetabbrev='sourceconversionBMPs', getcolumn='BMPShortName',
                                            by='FromLoadSource', equalto=row.LoadSource)
            thesebmps = thesebmps.str.lower().unique()
            totalnumbmps += thesebmps.size
            bmplist.append(thesebmps)
        self.geo_seg_source_bmps['eligible_landconversion_bmps'] = bmplist
        print('total no. of eligible "land conversion" BMPs: <%d>' % totalnumbmps)

        print(self.geo_seg_source_bmps.head())
        #print(bmplist[0])
