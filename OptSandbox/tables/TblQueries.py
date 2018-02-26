from tables.ExcelDataTable import ExcelDataTable


class TblQuery:
    def __init__(self, tables=None):
        """Wrapper for TblLoader instances. Provides methods for querying tables

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

    def get_agency_names_bygeoarea(self):  # TODO: make this get subset by area, instead of just all agencies.
        mylist = list(self.tables.srcdata.agencies['Agency'].unique())
        return mylist

    def get_all_agency_names(self):
        mylist = list(self.tables.srcdata.agencies['Agency'].unique())
        return mylist

    def get_all_sector_names(self):
        mylist = list(self.tables.srcdata.lsdefinitions['Sector'].unique())
        return mylist
