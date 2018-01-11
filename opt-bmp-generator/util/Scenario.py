import pandas as pd
import numpy as np

from util.TblLoader import TblLoader
from util.OptionLoader import OptionLoader


class Scenario:
    def __init__(self, optionsfile=''):
        """A wrapper to generate and hold the metadata for a scenario

        :param optionsfile:
        """
        # Load the Source Data and Base Condition tables
        self.tables = TblLoader()
        #self.load_source_and_base()

        # The scenario options (particular geographic region(s), agencies, etc.) are loaded for this scenario.
        self.options = OptionLoader(optionsfile=optionsfile, srcdataobj=self.tables.srcdata)

        # Options are used to query the BaseCondition data and filter only Load Sources with the chosen characteristics
        self.chosen_load_sources = None
        self.baseconquery()
        #print(self.chosen_load_sources.head())

        # Get the list of BMPs available on the chosen load sources
        self.geo_seg_source_bmps = None
        self.bmpquery()

        print('<Scenario Loading Complete>')

    # Python code to remove duplicate elements
    @staticmethod
    def removedups(listwithduplicates):
        final_list = []
        for num in listwithduplicates:
            if num not in final_list:
                final_list.append(num)
        return final_list

    def baseconquery(self):
        """Find the load sources (with non-zero acreage) in the specified agency-sector-segments

        :return:
        """
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
                booldf[h] = self.tables.basecond.LSacres[h].isin(optionscolumn)

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
        nonzero_ls_bool = self.tables.basecond.LSacres['PreBMPAcres'] != 0
        print('Load sources for chosen geo+agency+sector region with >0 acres: %d' % np.sum(optionsbool & nonzero_ls_bool))

        self.chosen_load_sources = self.tables.basecond.LSacres.loc[optionsbool & nonzero_ls_bool, :]

    def bmpquery(self):
        # Get all the BMPs that are possible on the set of Load sources
        #booldf = pd.DataFrame()
        #booldf[h] = self.baseconditionobj.LSacres[h].isin(optionscolumn)
        self.geo_seg_source_bmps = self.chosen_load_sources.copy()

        print('geo_seg_source_bmps:')
        print(self.geo_seg_source_bmps.head())
        print(':geo_seg_source_bmps')

        # All BMPs (by the load source group page info)
        bmplistoflists = []  # Create a Series to store the data
        totalnumbmps = 0
        for index, row in self.chosen_load_sources.iterrows():  # iterate through the load sources
            # Get the Load Source groups that this Load source is in.
            theseLSgroups = self.tables.srcdata.get(sheetabbrev='loadsourcegroupcomponents',
                                                    getcolumn='LoadSourceGroup', by='LoadSource',
                                                    equalto=row.LoadSource)  # pandas.core.series.Series

            bmplist = []  # Create a list to store the data
            for x in theseLSgroups:
                # Get the BMPs that can be applied on this load source group
                thesebmps = self.tables.srcdata.get(sheetabbrev='loadsourcegroups', getcolumn='BmpShortName',
                                                    by='LoadSourceGroup', equalto=x).tolist()
                #bmplist.append(thesebmps)
                bmplist += thesebmps
            bmplist = self.removedups(bmplist)
            totalnumbmps += len(bmplist)
            #print('"bmplist" has %d BMPs for load source "%s"' % (len(bmplist), row.LoadSource))
            #print(bmplist)
            #print(set(bmplist))
            #print('"bmplist" as a set has %d BMPs for load source "%s"' % (len(set(bmplist)), row.LoadSource))
            bmplistoflists.append(bmplist)

        print('The shape of "bmpSeries" is: %d' % len(bmplistoflists))
        self.geo_seg_source_bmps['eligible_bmps'] = bmplistoflists
        print('total no. of eligible BMPs: <%d>' % totalnumbmps)


        df = self.tables.srcdata['efficiencyBMPs']
        df['BMPShortName'] = df['BMPShortName'].str.lower()
        print(df.head())
        df = df.drop_duplicates(subset=['BMPShortName'])
        # Efficiency BMPs
        bmplist = []  # Create a list to store the data
        totalnumbmps = 0
        for index, row in self.chosen_load_sources.iterrows():
            thesebmps = df[df['BMPShortName'].notnull() & (df['LoadSource'] == row.LoadSource)]['BMPShortName']

            #thesebmps = self.tables.srcdata.get(sheetabbrev='efficiencyBMPs', getcolumn='BMPShortName',
            #                                    by='LoadSource', equalto=row.LoadSource)
            thesebmps = thesebmps.str.lower().unique()
            totalnumbmps += thesebmps.size
            bmplist.append(thesebmps)
        self.geo_seg_source_bmps['eligible_efficiency_bmps'] = bmplist
        print('total no. of eligible "efficiency" BMPs: <%d>' % totalnumbmps)

        # Land Conversion BMPs
        bmplist = []
        totalnumbmps = 0
        for index, row in self.chosen_load_sources.iterrows():
            thesebmps = self.tables.srcdata.get(sheetabbrev='sourceconversionBMPs', getcolumn='BMPShortName',
                                                by='FromLoadSource', equalto=row.LoadSource)
            thesebmps = thesebmps.str.lower().unique()
            totalnumbmps += thesebmps.size
            bmplist.append(thesebmps)
        self.geo_seg_source_bmps['eligible_landconversion_bmps'] = bmplist
        print('total no. of eligible "land conversion" BMPs: <%d>' % totalnumbmps)


        # Animal BMPs
        # TODO: Get data from BaseCondition 'Animal Counts' spreadsheet

        # Manure BMPs
        # TODO: Get data from ManureTonsProduced spreadsheet

        # Septic Systems
        # TODO: Get data from BaseCondition 'Septic Systems' spreadsheet

        print(self.geo_seg_source_bmps.head())
        #print(bmplist[0])
