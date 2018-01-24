import pandas as pd


class GeoSpec:
    def __init__(self, optionloaderobj=None, tables=None):
        """Determine the complete list of lrsegs, counties, states, etc. to be included in this Scenario

        Using the options/headers, query the SourceData table to generate a table with inclusive Series
        that can be used as boolean masks on other Series
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

        # A logical AND between the geo-options result and the non-geo-options is computed.
        self.geo_include_table = geodf.loc[geooptionsbool, :].copy()
        self.geo_include_table.to_csv('testwrite_geo_include_table.csv')
        print('Number of lrsegs included: %d' % geooptionsbool.sum())
