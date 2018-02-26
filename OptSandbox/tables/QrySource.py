import pandas as pd


class QrySource:
    def __init__(self, tables=None):
        """Wrapper for Source Data table. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """
        self.tables = tables

    def get_base_year_names(self):
        mylist = list(range(1995, 2016))
        return mylist

    def get_base_condition_names(self):
        mylist = ['Example_BaseCond1', 'Example_BaseCond2', 'Example_BaseCond3', 'Example_BaseCond4']
        return mylist

    def get_wastewaterdata_names(self):
        mylist = ['Example_WW1', 'Example_WW2', 'Example_WW3', 'Example_WW4']
        return mylist

    def get_costprofile_names(self):
        mylist = ['Example_CostProfile1', 'Example_CostProfile2', 'Example_CostProfile3', 'Example_CostProfile4']
        return mylist

    def get_geoscale_names(self):
        mylist = ['Chesapeake Bay Watershed', 'County', 'State', 'LandRiverSegment', 'County-Area in CBWS only']
        return mylist

    def get_geoarea_names(self, scale=None):
        if not scale:
            raise ValueError('Geo Scale must be specified to get area names')
        if scale == 'Chesapeake Bay Watershed':
            mylist = ['Chesapeake Bay Watershed']
        elif scale == 'County':
            mylist = self.tables.srcdata.georefs['CountyName'].unique()
        elif scale == 'State':
            mylist = self.tables.srcdata.georefs['StateAbbreviation'].unique()
        elif scale == 'StateAbbreviation':
            mylist = self.tables.srcdata.georefs['StateAbbreviation'].unique()
        elif scale == 'StateBasin':
            mylist = self.tables.srcdata.georefs['StateBasin'].unique()
        elif scale == 'MajorBasin':
            mylist = self.tables.srcdata.georefs['MajorBasin'].unique()
        elif scale == 'LandRiverSegment':
            mylist = self.tables.srcdata.georefs['LandRiverSegment'].unique()
        else:
            Warning('Specified scale "%s" is unrecognized' % scale)
            mylist = []
        return list(mylist)

    def get_lrseg_table(self, scale=None, areanames=None):
        """Determine the lrsegs (w/ names of counties, states, etc.) included in the specified geographic scale/areas

        Queries the SourceData table with a pd.Series that can be used as boolean mask

        Args:
            scale (str): Name of the geographic scale specified (e.g. 'County')
            areanames (list of str): Names of the geographic areas specified (e.g. ['Anne Arundel', 'York'])
        """
        geodf = self.tables.srcdata.georefs

        if not scale:
            raise ValueError('Geo Scale must be specified to get area names')
        if scale == 'Chesapeake Bay Watershed':
            booldf = pd.Series(True for _ in range(geodf.shape[0]))
        elif scale == 'County':
            booldf = geodf['CountyName'].isin(areanames)
        elif scale == 'State':
            booldf = geodf['StateAbbreviation'].isin(areanames)
        elif scale == 'StateAbbreviation':
            booldf = geodf['StateAbbreviation'].isin(areanames)
        elif scale == 'StateBasin':
            booldf = geodf['StateBasin'].isin(areanames)
        elif scale == 'MajorBasin':
            booldf = geodf['MajorBasin'].isin(areanames)
        elif scale == 'LandRiverSegment':
            booldf = geodf['LandRiverSegment'].isin(areanames)
        else:
            raise ValueError('Specified scale "%s" is unrecognized' % scale)

        my_geo_table = geodf.loc[booldf, :].copy()
        my_geo_table.to_csv('./output/testwrite_IncludeSpec_geo_include_table2.csv')
        print(my_geo_table.head())
        print('Number of lrseg records included: %d' % booldf.sum())

    def get_agencies_in_lrsegs(self, lrsegs=None):  # TODO: make this get subset by area, instead of just all agencies.
        """Determines the complete list of agencies to be included in this Scenario.

        Using the options/headers, query the SourceData table to set the 'self.agency' variable to be a table
        with inclusive Series that can be used as boolean masks on other Series

        Args:
            optionloaderobj (obj): An open OptionLoader instance.
            tables (obj): A TblLoader instance.
        """
        agencydf = self.tables.srcdata.agencies
        # Generate boolean mask for the dataframe based on the option specifications
        optionscolumn = optionloaderobj.options['AgencyCode']
        if (optionscolumn[0] == 'all') | optionscolumn.isnull().values.all():
            # just get all of the values
            self.agency = agencydf.loc[:, 'AgencyCode'].copy()
        else:
            boolSeries = pd.Series()
            # generate boolean mask for each basecondition row, if its value is in this options column
            boolSeries['AgencyCode'] = agencydf['AgencyCode'].isin(optionscolumn)
            self.agency = agencydf.loc[boolSeries, 'AgencyCode'].copy()
        self.agency.to_csv('./output/testwrite_IncludeSpec_agency_include_table.csv')
        print('Number of agencies included: %d' % len(self.agency))

        #mylist = list(self.tables.srcdata.agencies['Agency'].unique())
        #return mylist

    def get_all_agency_names(self):
        mylist = list(self.tables.srcdata.agencies['Agency'].unique())
        return mylist

    def get_all_sector_names(self):
        mylist = list(self.tables.srcdata.lsdefinitions['Sector'].unique())
        return mylist
