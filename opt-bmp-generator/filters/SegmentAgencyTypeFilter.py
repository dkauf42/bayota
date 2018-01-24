import pandas as pd
import numpy as np


class SegmentAgencyTypeFilter:
    def __init__(self, optionloaderobj=None, tables=None):
        """Find the segment - agency - source combinations available in the specified options."""

        self.all_sat = None
        self.sat_indices = None
        self.filter_from_options(optionloaderobj, tables.basecond)

    def filter_from_options(self, optionsobj, baseobj):
        """Find the load sources (with non-zero acreage) in the specified agency-sector-segments

            option headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
                             OutOfCBWS, AgencyCode, Sector
        """
        # Land Use Acres
        # Generate boolean mask for the Base Conditions spreadsheet based on the option specifications
        oh = optionsobj.headers
        booldf = pd.DataFrame()
        for h in oh:
            optionscolumn = optionsobj.options[h]
            if (optionscolumn[0] == 'all') | optionscolumn.isnull().values.all():
                # exclude this column from the boolean dataframe if we're just going to get all of the values
                pass
            else:
                # generate boolean for each basecondition row, if its value is in this options column
                booldf[h] = baseobj.LSacres[h].isin(optionscolumn)

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
        self.all_sat = baseobj.LSacres.loc[optionsbool, ['LandRiverSegment', 'AgencyCode', 'LoadSource']].copy()
        self.all_sat = self.all_sat.set_index(['LandRiverSegment', 'AgencyCode'])
        self.all_sat.to_csv('testwrite_allsegsources.csv')
        print('All seg+agency specific load sources: %d' % np.sum(optionsbool))

        self.sat_indices = baseobj.LSacres.loc[optionsbool, ['LandRiverSegment', 'AgencyCode', 'LoadSource']].copy()
        self.sat_indices = self.sat_indices.set_index(['LandRiverSegment', 'AgencyCode', 'LoadSource'])
        self.sat_indices.to_csv('testwrite_sat_indices.csv')

        # TODO: Septic Systems

        # TODO: Animals
