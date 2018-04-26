import numpy as np

from sandbox.util.Jeeves.sourcehooks import SourceHook


class Translator(SourceHook):
    def __init__(self):
        """ Sector Methods """
        SourceHook.__init__(self)

    # Translation methods (from IDs to NAMEs)
    def translate_slabidtable_to_slabnametable(self, slabidtable=None):
        newtable = slabidtable.copy()

        # Get relevant source data tables
        TblLandRiverSegment = self.source.TblLandRiverSegment
        TblState = self.source.TblState
        TblAgency = self.source.TblAgency
        TblLoadSource = self.source.TblLoadSource
        TblBmp = self.source.TblBmp

        # Translate lrsegid to GeographyName
        columnmask = ['landriversegment', 'stateid', 'lrsegid']
        newtable = TblLandRiverSegment.loc[:, columnmask].merge(newtable, how='inner')
        columnmask = ['stateabbreviation', 'stateid']
        newtable = TblState.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to Agency codes
        columnmask = ['agencycode', 'agencyid']
        newtable = TblAgency.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to LoadSource names
        columnmask = ['loadsource', 'loadsourceid']
        newtable = TblLoadSource.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to BMP names
        columnmask = ['bmpshortname', 'bmpid']
        newtable = TblBmp.loc[:, columnmask].merge(newtable, how='inner')

        newtable.drop(['lrsegid', 'stateid', 'agencyid', 'loadsourceid', 'bmpid', 'unitid'], axis=1, inplace=True)
        newtable.rename(columns={'landriversegment': 'GeographyName',
                                 'stateabbreviation': 'StateAbbreviation',
                                 'agencycode': 'AgencyCode',
                                 'loadsource': 'LoadSourceGroup',
                                 'bmpshortname': 'BmpShortname'}, inplace=True)

        newtable['Unit'] = 'Percent'

        if 'Amount' in newtable.columns:
            newtable['StateUniqueIdentifier'] = np.nan
            # Reorder columns to match CAST input table format
            newtable = newtable[['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                 'GeographyName', 'LoadSourceGroup', 'Amount', 'Unit']]

        return newtable


    def translate_scabidtable_to_scabnametable(self, scabidtable=None):
        newtable = scabidtable.copy()

        # Get relevant source data tables
        TblCounty = self.source.TblCounty
        TblAnimalGroup = self.source.TblAnimalGroup
        TblAgency = self.source.TblAgency
        TblLoadSource = self.source.TblLoadSource
        TblBmp = self.source.TblBmp
        TblLoadSourceGroup = self.source.TblLoadSourceGroup

        # Translate countyid to GeographyName (FIPS) and add stateabbreviation
        columnmask = ['countyid', 'stateabbreviation', 'fips']
        newtable = TblCounty.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to Agency codes
        columnmask = ['agencycode', 'agencyid']
        newtable = TblAgency.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to LoadSourceGroup names
        columnmask = ['loadsourcegroup', 'loadsourcegroupid']
        newtable = TblLoadSourceGroup.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to BMP names
        columnmask = ['bmpshortname', 'bmpid']
        newtable = TblBmp.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to AnimalGroup names
        columnmask = ['animalgroupid', 'animalgroup']
        newtable = TblAnimalGroup.loc[:, columnmask].merge(newtable, how='inner')

        newtable.drop(['countyid', 'agencyid', 'loadsourcegroupid', 'bmpid',
                       'animalgroupid', 'animalid', 'baseconditionid'], axis=1, inplace=True)
        newtable.rename(columns={'fips': 'GeographyName',
                                 'stateabbreviation': 'StateAbbreviation',
                                 'agencycode': 'AgencyCode',
                                 'loadsourcegroup': 'LoadSourceGroup',
                                 'bmpshortname': 'BmpShortname',
                                 'animalgroup': 'AnimalGroup'}, inplace=True)

        newtable['Unit'] = 'Percent'

        if 'Amount' in newtable.columns:
            newtable['StateUniqueIdentifier'] = np.nan
            newtable['NReductionFraction'] = np.nan
            newtable['PReductionFraction'] = np.nan
            # Reorder columns to match CAST input table format
            newtable = newtable[['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                 'GeographyName', 'AnimalGroup', 'LoadSourceGroup', 'Amount', 'Unit',
                                 'NReductionFraction', 'PReductionFraction']]

        return newtable


    def translate_sftabidtable_to_sftabnametable(self, sftabidtable=None):
        newtable = sftabidtable.copy()

        # Get relevant source data tables
        TblCounty = self.source.TblCounty
        TblAnimalGroup = self.source.TblAnimalGroup
        TblAgency = self.source.TblAgency
        TblLoadSource = self.source.TblLoadSource
        TblBmp = self.source.TblBmp
        TblLoadSourceGroup = self.source.TblLoadSourceGroup

        # Translate countyid to FIPSFrom and then FIPSTo (and add stateabbreviation)
        columnmask = ['countyid', 'stateabbreviation', 'fips']
        newtable = TblCounty.loc[:, columnmask].merge(newtable, how='inner',
                                                      left_on='countyid',
                                                      right_on='countyidFrom')
        newtable.drop(['countyid', 'countyidFrom'], axis=1, inplace=True)
        newtable.rename(columns={'fips': 'FIPSFrom'}, inplace=True)

        # For countyidTo's that are blank (meaning transport out of the watershed),
        # we need special consideration and use a RIGHT OUTER JOIN instead of an INNER JOIN.
        columnmask = ['countyid', 'fips']
        newtable = TblCounty.loc[:, columnmask].merge(newtable, how='right',
                                                      left_on='countyid',
                                                      right_on='countyidTo')
        newtable.drop(['countyid', 'countyidTo'], axis=1, inplace=True)
        newtable.rename(columns={'fips': 'FIPSTo'}, inplace=True)
        # Also because there are NaNs, the merge converts the data type to float instead of integer.
        # So let's remove the NaNs and then remove the unnecessary decimal points
        newtable['FIPSTo'] = newtable['FIPSTo'].replace(np.nan, '', regex=True)
        newtable['FIPSTo'] = newtable['FIPSTo'].astype(dtype=str).replace('\.0', '', regex=True)

        # Translate to Agency codes
        columnmask = ['agencycode', 'agencyid']
        newtable = TblAgency.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to LoadSourceGroup names
        columnmask = ['loadsourcegroup', 'loadsourcegroupid']
        newtable = TblLoadSourceGroup.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to BMP names
        columnmask = ['bmpshortname', 'bmpid']
        newtable = TblBmp.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to AnimalGroup names
        columnmask = ['animalgroupid', 'animalgroup']
        newtable = TblAnimalGroup.loc[:, columnmask].merge(newtable, how='inner')

        newtable.drop(['agencyid', 'loadsourcegroupid', 'bmpid',
                       'animalgroupid', 'animalid', 'baseconditionid'], axis=1, inplace=True)
        newtable.rename(columns={'stateabbreviation': 'StateAbbreviation',
                                 'agencycode': 'AgencyCode',
                                 'loadsourcegroup': 'LoadSourceGroup',
                                 'bmpshortname': 'BmpShortname',
                                 'animalgroup': 'AnimalGroup'}, inplace=True)

        newtable['Unit'] = 'Percent'

        if 'Amount' in newtable.columns:
            newtable['StateUniqueIdentifier'] = np.nan
            # Reorder columns to match CAST input table format
            newtable = newtable[['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                 'FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup', 'Amount', 'Unit']]

        return newtable