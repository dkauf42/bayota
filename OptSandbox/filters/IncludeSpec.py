import pandas as pd


class IncludeSpec:
    def __init__(self, optionloaderobj=None, tables=None):
        """Determine the complete list of geographic and non-geographic entities to be included in this Scenario
        Parameters
        ----------
        optionloaderobj : `obj`

        tables : `obj`


        Attributes
        ----------
        geo : `pandas dataframe`
            geographic elements to be included in this Scenario. The following columns are included:
            LRSeg, FIPS, CountyName, StateAbbreviation, OutOfCBWS,\
            ChesapeakeBaySegment, MajorBasin, MinorBasin, StateBasin.

        agency : `pandas dataframe`
            agencies to be included in this Scenario (Pandas.DataFrame).
        """

        self.geo = None
        self._generate_geo(optionloaderobj, tables)

        self.agency = None
        self._generate_agency(optionloaderobj, tables)

    def _generate_geo(self, optionloaderobj, tables):
        """Determines the complete list of lrsegs, counties, states, etc. to be included in this Scenario.

        Using the options/headers, query the SourceData table to set the 'self.geo' variable to be a table
        with inclusive Series that can be used as boolean masks on other Series.

        Args:
            optionloaderobj: An open OptionLoader instance.
            tables: A TblLoader instance.
        """
        geodf = tables.srcdata.georefs

        # Generate boolean mask for the dataframe based on the option specifications
        # i.e. loop through headers specified in the options file
        oh = optionloaderobj.headers
        booldf = pd.DataFrame()
        for h in oh:
            optionscolumn = optionloaderobj.options[h]
            if (optionscolumn[0] == 'all') | optionscolumn.isnull().values.all():
                # exclude this column from the boolean dataframe mask if we're just going to get all of the values
                pass
            else:
                # generate boolean mask for each basecondition row, if its value is in this options column
                booldf[h] = geodf[h].isin(optionscolumn)

        geo_options_list = ('LandRiverSegment', 'CountyName', 'StateAbbreviation', 'StateBasin')

        # A logical OR amongst the geographic options is computed.
        geooptionsbooldf = booldf[booldf.columns[booldf.columns.isin(geo_options_list)]]
        geooptionsbool = geooptionsbooldf.any(axis=1)
        self.geo = geodf.loc[geooptionsbool, :].copy()
        self.geo.to_csv('./output/testwrite_IncludeSpec_geo_include_table.csv')
        print('Number of lrsegs included: %d' % geooptionsbool.sum())

    def _generate_agency(self, optionloaderobj, tables):
        """Determines the complete list of agencies to be included in this Scenario.

        Using the options/headers, query the SourceData table to set the 'self.agency' variable to be a table
        with inclusive Series that can be used as boolean masks on other Series

        Args:
            optionloaderobj: An open OptionLoader instance.
            tables: A TblLoader instance.
        """
        agencydf = tables.srcdata.agencies
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
