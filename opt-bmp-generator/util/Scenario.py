import pandas as pd
import numpy as np

from util.TblLoader import TblLoader
from util.OptionLoader import OptionLoader
from util.SasFilter import SasFilter


class Scenario:
    def __init__(self, optionsfile=''):
        """A wrapper to generate and hold the metadata for a scenario

        :param optionsfile:
        """
        # Load the Source Data and Base Condition tables
        self.tables = TblLoader()

        # The scenario options (particular geographic region(s), agencies, etc.) are loaded for this scenario.
        self.options = OptionLoader(optionsfile=optionsfile, srcdataobj=self.tables.srcdata)

        # Options are used to query the BaseCondition data and filter only Load Sources with the chosen characteristics
        self.sas = SasFilter(OptionLoaderObj=self.options, BaseConditionObj=self.tables.basecond)

        # Get the list of BMPs available on the chosen load sources
        self.geo_seg_source_bmps = None
        self.filterbmpsby_sas()
        print('<Scenario Loading Complete>')

    def filterbmpsby_sas(self):
        # Get all the BMPs that are possible on the set of Load sources
        self.geo_seg_source_bmps = self.sas.chosen_load_sources.copy()
        bmplistoflists = []  # Create a list to store the data
        bmptypeslistoflists = []
        overallbmplist = []
        totalnumbmps = 0
        for index, row in self.sas.chosen_load_sources.iterrows():  # iterate through the load sources
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
            bmplistoflists.append(bmplist)
            totalnumbmps += len(bmplist)
            thesebmptypes = self.tables.srcdata.findbmptype(bmplist)  # For each BMP, figure out which type it is
            bmptypeslistoflists.append(thesebmptypes)
            # print('"bmplist" has %d BMPs for load source "%s"' % (len(bmplist), row.LoadSource))
            overallbmplist += bmplist

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

    @staticmethod
    def removedups(listwithduplicates):
        """ Python code to remove duplicate elements"""
        final_list = []
        for num in listwithduplicates:
            if num not in final_list:
                final_list.append(num)
        return final_list
