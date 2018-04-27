import pandas as pd
from itertools import product
from itertools import permutations

from sandbox.util.jeeves.sourcehooks.sourcehooks import SourceHook


class Bmp(SourceHook):
    def __init__(self, sourcedata=None):
        """ BMP Methods """
        SourceHook.__init__(self, sourcedata=sourcedata)

    def all_names(self):
        TblBmp = self.source.TblBmp  # get relevant source data]
        return TblBmp.loc[:, 'bmpshortname']

    def names_from_ids(self, bmpids=None):
        bmpids = self.forceToSingleColumnDataFrame(bmpids, colname='bmpid')
        return self.singleconvert(sourcetbl='TblBmp', toandfromheaders=['bmpshortname', 'bmpid'],
                                  fromtable=bmpids, toname='bmpshortname')

    def single_bmpid_from_shortname(self, bmpshortname):
        TblBmp = self.source.TblBmp  # get relevant source data
        return TblBmp['bmpid'][TblBmp['bmpshortname'] == bmpshortname].tolist()

    def bmpids_from_categoryids(self, categoryids):
        categoryids = self.forceToSingleColumnDataFrame(categoryids, colname='bmpcategoryid')
        return self.singleconvert(sourcetbl='TblBmp', toandfromheaders=['bmpcategoryid', 'bmpid'],
                                  fromtable=categoryids, toname='bmpid')

    def land_slabidtable_from_SourceLrsegAgencyIDtable(self, SourceLrsegAgencyIDtable):
        TblBmpLoadSourceFromTo = self.source.TblBmpLoadSourceFromTo

        TblBmpLoadSourceFromTo.rename(columns={'fromloadsourceid': 'loadsourceid'}, inplace=True)
        columnmask = ['bmpid', 'loadsourceid']
        tblsubset = TblBmpLoadSourceFromTo.loc[:, columnmask].merge(SourceLrsegAgencyIDtable, how='inner')

        return tblsubset
        # return SourceLrsegAgencyIDtable

    def animal_scabidtable_from_SourceCountyAgencyIDtable(self, SourceCountyAgencyIDtable, baseconditionid=None):
        TblAnimalPopulation = self.source.TblAnimalPopulation
        TblAnimalGroupAnimal = self.source.TblAnimalGroupAnimal
        TblBmpAnimalGroup = self.source.TblBmpAnimalGroup
        TblAgency = self.source.TblAgency
        TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource

        sca_table = SourceCountyAgencyIDtable.copy()

        # For Animals, only the NONFED agency matters, so remove all rows with agencies not equal to NONFED
        nonfedid = TblAgency['agencyid'][TblAgency['agencycode'] == 'NONFED'].values[0]
        sca_table = sca_table[sca_table["agencyid"] == nonfedid]

        # Baseconditionid is needed for indexing with the AnimalPopulation table, so and a column for it to the SCAtable
        sca_table['baseconditionid'] = baseconditionid.baseconditionid.tolist()[0]

        # Get which animals are present in the county, agency, loadsources
        columnmask = ['baseconditionid', 'countyid', 'loadsourceid', 'animalid', 'animalcount', 'animalunits']
        tblsubset = TblAnimalPopulation.loc[:, columnmask].merge(sca_table, how='inner')

        # BMPs are associated with AnimalGroupIDs not AnimalIDs
        # Get the animalgroups that each animalid belongs to
        columnmask = ['animalgroupid', 'animalid']
        tblsubset = TblAnimalGroupAnimal.loc[:, columnmask].merge(tblsubset, how='inner')
        # Get the BMPs that can be applied to each animalgroupid
        columnmask = ['animalgroupid', 'bmpid']
        tblsubset = TblBmpAnimalGroup.loc[:, columnmask].merge(tblsubset, how='inner')
        tblsubset.drop(['animalgroupid'], axis=1, inplace=True)
        tblsubset.drop_duplicates(inplace=True)

        # Convert loadsourceids to loadsourcegroupids
        columnmask = ['loadsourcegroupid', 'loadsourceid']
        tblsubset = TblLoadSourceGroupLoadSource.loc[:, columnmask].merge(tblsubset, how='inner')
        tblsubset.drop(['loadsourceid'], axis=1, inplace=True)

        return tblsubset

    def manure_sftabidtable_from_SourceFromToAgencyIDtable(self, SourceCountyAgencyIDtable, baseconditionid=None):
        TblAnimalPopulation = self.source.TblAnimalPopulation
        TblAnimalGroupAnimal = self.source.TblAnimalGroupAnimal
        TblBmpAnimalGroup = self.source.TblBmpAnimalGroup
        TblBmp = self.source.TblBmp
        TblAgency = self.source.TblAgency
        TblLoadSource = self.source.TblLoadSource
        TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource

        sca_table = SourceCountyAgencyIDtable.copy()

        # Baseconditionid is needed for indexing with the AnimalPopulation table, so and a column for it to the SCAtable
        sca_table['baseconditionid'] = baseconditionid.baseconditionid.tolist()[0]

        # For Manure, only the NONFED agency matters, so remove all rows with agencies not equal to NONFED
        nonfedid = TblAgency['agencyid'][TblAgency['agencycode'] == 'NONFED'].values[0]
        sca_table = sca_table[sca_table["agencyid"] == nonfedid]

        # For Manure, only the "Non-Permitted Feeding Space" and "Permitted Feeding Space" load sources matter,
        # so remove all rows with loadsources not equal to them
        npfsid = TblLoadSource['loadsourceid'][TblLoadSource['loadsource'] == 'Non-Permitted Feeding Space'].values[0]
        pfsid = TblLoadSource['loadsourceid'][TblLoadSource['loadsource'] == 'Permitted Feeding Space'].values[0]
        # Why use both feeding space types?  Answer from Olivia:
        # The two feeding spaces have "the same effect in that the manure has the same concentrations.
        # But there are different amounts of manure on permitted vs. non-permitted.
        # If you specified only one, then you would be missing some amount of manure."
        allowed_loadsource_list = [npfsid, pfsid]
        sca_table = sca_table.loc[sca_table['loadsourceid'].isin(allowed_loadsource_list)]
        countylist = sca_table.countyid.unique()

        # For Manure, calculate all of the From-To permutations
        allbetweencountyperms = list(permutations(countylist, 2))
        alloutofwatersheds = list(product(countylist, ['']))  # a blank represents transport out of the watershed
        zser = pd.Series(allbetweencountyperms + alloutofwatersheds)
        sfta_table = zser.apply(pd.Series)
        sfta_table.columns = ['countyidFrom', 'countyidTo']
        sca_table['countyidFrom'] = sca_table['countyid']  # duplicate countyid column with the countyidFrom name
        columnmask = ['countyidFrom', 'countyidTo']
        sfta_table = sfta_table.loc[:, columnmask].merge(sca_table, how='inner')

        # Get which animals are present in the county, agency, loadsources
        columnmask = ['baseconditionid', 'countyid', 'loadsourceid', 'animalid', 'animalcount', 'animalunits']
        tblsubset = TblAnimalPopulation.loc[:, columnmask].merge(sfta_table, how='inner')
        tblsubset.drop(['countyid'], axis=1, inplace=True)

        # # Get the animalgroups that each animalid belongs to
        # columnmask = ['animalgroupid', 'animalid']
        # tblsubset = TblAnimalGroupAnimal.loc[:, columnmask].merge(tblsubset, how='inner')

        # # Get the BMPs that can be applied to each animalgroupid
        # columnmask = ['animalgroupid', 'bmpid']
        # tblsubset = TblBmpAnimalGroup.loc[:, columnmask].merge(tblsubset, how='inner')

        # For Manure transport, there's only one bmp that should be applied (?) TODO: check that this is true
        mtid = TblBmp['bmpid'][TblBmp['bmpshortname'] == 'ManureTransport'].values[0]
        tblsubset['bmpid'] = mtid

        # Convert loadsourceids to loadsourcegroupids
        columnmask = ['loadsourcegroupid', 'loadsourceid']
        tblsubset = TblLoadSourceGroupLoadSource.loc[:, columnmask].merge(tblsubset, how='inner')
        tblsubset.drop(['loadsourceid'], axis=1, inplace=True)

        return tblsubset

    def appendBmpSector_to_table_with_bmpid(self):
        pass

    def appendBmpType_to_table_with_bmpid(self):
        pass

    def appendBmpGroup_to_table_with_bmpid(self):
        pass