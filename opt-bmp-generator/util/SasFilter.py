import pandas as pd
import numpy as np


class SasFilter:
    def __init__(self, optionloaderobj=None, baseconditionobj=None):
        """A wrapper to generate and hold the metadata for a scenario

        :param optionsfile:
        """
        self.all_sas = None
        self.chosen_load_sources = None
        self.filter_from_options(optionloaderobj, baseconditionobj)
        # Load the Source Data and Base Condition tables

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
        self.all_sas = baseobj.LSacres.loc[optionsbool, ['LandRiverSegment', 'AgencyCode', 'LoadSource']].copy()
        self.all_sas = self.all_sas.set_index(['LandRiverSegment', 'AgencyCode'])
        self.all_sas.to_csv('testwrite_allsegsources.csv')
        print('All seg+agency region load sources: %d' % np.sum(optionsbool))

        # Wen can also only include load sources that have non-zero values.
        nonzero_ls_bool = baseobj.LSacres['PreBMPAcres'] != 0
        self.chosen_load_sources = baseobj.LSacres.loc[optionsbool & nonzero_ls_bool, :]
        print('Seg+agency region load sources with >0 pre-bmp acres: %d' % np.sum(optionsbool & nonzero_ls_bool))
        print('<BaseCondition Querying Complete>')

        # TODO: Septic Systems

        # TODO: Animals