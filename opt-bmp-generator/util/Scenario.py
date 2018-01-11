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
        self.allsegsources = None
        self.filtersegmentsfromoptions()
        #print(self.chosen_load_sources.head())

        # Get the list of BMPs available on the chosen load sources
        self.geo_seg_source_bmps = None
        self.filterbmpsbysegagencysources()
        print('<Scenario Loading Complete>')

    # Python code to remove duplicate elements
    @staticmethod
    def removedups(listwithduplicates):
        final_list = []
        for num in listwithduplicates:
            if num not in final_list:
                final_list.append(num)
        return final_list

    def filtersegmentsfromoptions(self):
        """Find the load sources (with non-zero acreage) in the specified agency-sector-segments

            option headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
                             OutOfCBWS, AgencyCode, Sector
        :return:
        """

        # Generate boolean mask for the Base Conditions spreadsheet based on the option specifications
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
        print('All load sources for chosen seg+agency region: %d' % np.sum(optionsbool))
        self.allsegsources = self.tables.basecond.LSacres.loc[optionsbool,
                                                              ['LandRiverSegment', 'AgencyCode', 'LoadSource']].copy()
        self.allsegsources = self.allsegsources.set_index(['LandRiverSegment', 'AgencyCode'])
        self.allsegsources.to_csv('testwrite_allsegsources.csv')

        # Wen can also only include load sources that have non-zero values.
        nonzero_ls_bool = self.tables.basecond.LSacres['PreBMPAcres'] != 0
        print('Load sources for chosen seg+agency region with >0 acres: %d' % np.sum(optionsbool & nonzero_ls_bool))
        self.chosen_load_sources = self.tables.basecond.LSacres.loc[optionsbool & nonzero_ls_bool, :]
        print('<BaseCondition Querying Complete>')

    def filterbmpsbysegagencysources(self):
        # Get all the BMPs that are possible on the set of Load sources
        self.geo_seg_source_bmps = self.chosen_load_sources.copy()
        bmplistoflists = []  # Create a list to store the data
        bmptypeslistoflists = []
        overallbmplist = []
        totalnumbmps = 0
        for index, row in self.chosen_load_sources.iterrows():  # iterate through the load sources
            # Get the Load Source groups that this Load source is in.
            loadsourcegroups = self.tables.srcdata.get(sheetabbrev='loadsourcegroupcomponents',
                                                       getcolumn='LoadSourceGroup', by='LoadSource',
                                                       equalto=row.LoadSource)  # pandas.core.series.Series

            bmplist = []  # Create a list to store the data
            for x in loadsourcegroups:  # iterate through the load source groups
                # Get the BMPs that can be applied on this load source group
                thesebmps = self.tables.srcdata.get(sheetabbrev='loadsourcegroups', getcolumn='BmpShortName',
                                                    by='LoadSourceGroup', equalto=x).tolist()
                bmplist += thesebmps
            bmplist = self.removedups(bmplist)
            totalnumbmps += len(bmplist)
            overallbmplist += bmplist

            # For each BMP, figure out which type it is
            thesebmptypes = self.tables.srcdata.findbmptype(bmplist)

            #print('"bmplist" has %d BMPs for load source "%s"' % (len(bmplist), row.LoadSource))
            bmplistoflists.append(bmplist)
            bmptypeslistoflists.append(thesebmptypes)

        overallbmplist = self.removedups(overallbmplist)
        overallbmptypes = self.tables.srcdata.findbmptype(overallbmplist)
        print('length of overall bmp list: %d' % len(overallbmplist))
        print(overallbmplist)
        print(overallbmptypes)

        self.geo_seg_source_bmps['eligible_bmps'] = bmplistoflists
        self.geo_seg_source_bmps['eligible_bmps_types'] = bmptypeslistoflists
        print('total no. of eligible BMPs: <%d>' % totalnumbmps)


        # # Efficiency BMPs
        # df = self.tables.srcdata['efficiencyBMPs']
        # df['BMPShortName'] = df['BMPShortName'].str.lower()
        # df = df.drop_duplicates(subset=['BMPShortName'])
        # bmplist = []  # Create a list to store the data
        # totalnumbmps = 0
        # for index, row in self.chosen_load_sources.iterrows():
        #     thesebmps = df[df['BMPShortName'].notnull() & (df['LoadSource'] == row.LoadSource)]['BMPShortName']
        #     #thesebmps = self.tables.srcdata.get(sheetabbrev='efficiencyBMPs', getcolumn='BMPShortName',
        #     #                                    by='LoadSource', equalto=row.LoadSource)
        #     thesebmps = thesebmps.str.lower().unique()
        #     totalnumbmps += thesebmps.size
        #     bmplist.append(thesebmps)
        # self.geo_seg_source_bmps['eligible_efficiency_bmps'] = bmplist
        # print('total no. of eligible "efficiency" BMPs: <%d>' % totalnumbmps)
        #
        # # Land Conversion BMPs
        # df = self.tables.srcdata['sourceconversionBMPs']
        # df['BMPShortName'] = df['BMPShortName'].str.lower()
        # df = df.drop_duplicates(subset=['BMPShortName'])
        # bmplist = []
        # totalnumbmps = 0
        # for index, row in self.chosen_load_sources.iterrows():
        #     thesebmps = df[df['BMPShortName'].notnull() & (df['FromLoadSource'] == row.LoadSource)]['BMPShortName']
        #     #thesebmps = self.tables.srcdata.get(sheetabbrev='sourceconversionBMPs', getcolumn='BMPShortName',
        #     #                                    by='FromLoadSource', equalto=row.LoadSource)
        #     thesebmps = thesebmps.str.lower().unique()
        #     totalnumbmps += thesebmps.size
        #     bmplist.append(thesebmps)
        # self.geo_seg_source_bmps['eligible_landconversion_bmps'] = bmplist
        # print('total no. of eligible "land conversion" BMPs: <%d>' % totalnumbmps)

        # Load Reudction BMPs
        # TODO: Get data from

        # Animal BMPs
        # TODO: Get data from BaseCondition 'Animal Counts' spreadsheet

        # Manure BMPs
        # TODO: Get data from ManureTonsProduced spreadsheet

        # Septic Systems
        # TODO: Get data from BaseCondition 'Septic Systems' spreadsheet

        #print(self.geo_seg_source_bmps.head())
        #print(bmplist[0])
        self.geo_seg_source_bmps.to_csv('testwrite_geo_seg_source_bmps.csv')

