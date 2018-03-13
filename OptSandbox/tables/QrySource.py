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
            #mylist_counties = self.tables.srcdata.georefs['CountyName'].unique()
            #mylist_states = self.tables.srcdata.georefs['StateAbbreviation'].unique()
            df = self.tables.srcdata.georefs.loc[:, ['FIPS', 'CountyName', 'StateAbbreviation']].copy()
            df.drop_duplicates('FIPS', inplace=True)
            mylist_counties = df['CountyName']
            mylist_states = df['StateAbbreviation']

            mylist = ["{}, {}".format(a_, b_) for a_, b_ in zip(mylist_counties, mylist_states)]
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

            county_list, state_list = zip(*(s.split(", ") for s in areanames))

            booldf1 = geodf['CountyName'].isin(county_list)
            booldf2 = geodf['StateAbbreviation'].isin(state_list)
            booldf = booldf1 & booldf2
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

        #print(my_geo_table.head())
        #print('Number of lrseg records included: %d' % booldf.sum())

        return my_geo_table

    def get_all_agency_names(self):
        mylist = list(self.tables.srcdata.agencies['Agency'].unique())
        return mylist

    def get_all_sector_names(self):
        mylist = list(self.tables.srcdata.lsdefinitions['Sector'].unique())
        return mylist

    def get_dict_of_bmps_by_loadsource_keys(self, load_sources):
        """ Generate a dictionary of BMPs that are eligible for every load source

        Args:
            load_sources (pandas.Series):

        """
        mydict = {}
        for ls in load_sources:
            # Get Load Source Groups that this load source is in.
            loadsourcegroups = self.tables.srcdata.get(sheetabbrev='sourcegrpcomponents', getcolumn='LoadSourceGroup',
                                                       by='LoadSource', equalto=ls)  # pandas.core.series.Series

            bmplist = []
            for x in loadsourcegroups:
                # Get the BMPs that can be applied on this load source group
                bmplist += self.tables.srcdata.get(sheetabbrev='sourcegrps', getcolumn='BmpShortName',
                                                   by='LoadSourceGroup', equalto=x).tolist()
            mydict[ls] = self.removedups(bmplist)
        return mydict

    @staticmethod
    def removedups(listwithduplicates):
        seen = set()
        seen_add = seen.add
        return [x for x in listwithduplicates if not (x in seen or seen_add(x))]
