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

    def single_bmptype_from_bmpid(self, bmpid):
        TblBmp = self.source.TblBmp  # get relevant source data
        TblBmpType = self.source.TblBmpType  # get relevant source data

        typeid = TblBmp['bmptypeid'][TblBmp['bmpid'] == bmpid].tolist()
        return TblBmpType['bmptype'][TblBmpType['bmptypeid'] == typeid].tolist()

    def bmpids_from_categoryids(self, categoryids):
        categoryids = self.forceToSingleColumnDataFrame(categoryids, colname='bmpcategoryid')
        return self.singleconvert(sourcetbl='TblBmp', toandfromheaders=['bmpcategoryid', 'bmpid'],
                                  fromtable=categoryids, toname='bmpid')

    # Methods to append BMPids to loadsource tables
    def append_animal_bmpids(self, SourceCountyAgencyIDtable=None, baseconditionid=None):
        TblAnimalPopulation = self.source.TblAnimalPopulation
        TblAnimalGroupAnimal = self.source.TblAnimalGroupAnimal
        TblBmp = self.source.TblBmp
        TblBmpAnimalGroup = self.source.TblBmpAnimalGroup
        TblBmpType = self.source.TblBmpType
        TblAgency = self.source.TblAgency
        TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource

        sca_table = SourceCountyAgencyIDtable.copy()

        # For Animals, only the NONFED agency matters, so remove all rows with agencies not equal to NONFED
        nonfedid = TblAgency['agencyid'][TblAgency['agencycode'] == 'NONFED'].values[0]
        sca_table = sca_table[sca_table["agencyid"] == nonfedid]

        # Baseconditionid is needed for indexing with the AnimalPopulation table, so and a column for it to the SCAtable
        sca_table.loc[:, 'baseconditionid'] = int(baseconditionid['baseconditionid'])

        # Get which animals are present in the county, agency, loadsources
        columnmask = ['baseconditionid', 'countyid', 'loadsourceid', 'animalid', 'animalcount', 'animalunits']
        tblsubset = TblAnimalPopulation.loc[:, columnmask].merge(sca_table, how='inner')

        # BMPs are associated with AnimalGroupIDs not AnimalIDs
        # # Get the animalgroups that each animalid belongs to
        # columnmask = ['animalgroupid', 'animalid']
        # tblsubset = TblAnimalGroupAnimal.loc[:, columnmask].merge(tblsubset, how='inner')

        # Get the BMPs that can be applied to each animalgroupid
        # !! Use the table assumption that animalgroupid is equal to animalid for each individual animal !!
        columnmask = ['animalgroupid', 'bmpid']
        tblsubset = TblBmpAnimalGroup.loc[:, columnmask].merge(tblsubset, how='right',
                                                               left_on='animalgroupid', right_on='animalid')
        tblsubset.drop(['animalgroupid'], axis=1, inplace=True)
        tblsubset.drop_duplicates(inplace=True)

        # Remove those bmps that aren't of type "Animal Manure"
        animaltypeid = TblBmpType['bmptypeid'][TblBmpType['bmptype'] == 'Animal Manure'].values[0]
        columnmask = ['bmpid', 'bmptypeid']
        tblsubset = TblBmp.loc[:, columnmask].merge(tblsubset, how='inner')
        tblsubset = tblsubset.loc[tblsubset['bmptypeid'] == animaltypeid]
        tblsubset.drop(['bmptypeid'], axis=1, inplace=True)

        # Convert loadsourceids to loadsourcegroupids
        columnmask = ['loadsourcegroupid', 'loadsourceid']
        tblsubset = TblLoadSourceGroupLoadSource.loc[:, columnmask].merge(tblsubset, how='inner')
        tblsubset.drop(['loadsourceid'], axis=1, inplace=True)

        return tblsubset

    def append_land_bmpids(self, table_with_loadsourceids):
        TblBmpLoadSourceFromTo = self.source.TblBmpLoadSourceFromTo

        TblBmpLoadSourceFromTo.rename(columns={'fromloadsourceid': 'loadsourceid'}, inplace=True)
        columnmask = ['bmpid', 'loadsourceid']
        tblsubset = TblBmpLoadSourceFromTo.loc[:, columnmask].merge(table_with_loadsourceids, how='inner')

        return tblsubset

    def append_manure_bmpids(self, SourceFromToAgencyIDtable=None, baseconditionid=None):
        TblAnimalPopulation = self.source.TblAnimalPopulation
        TblAnimalGroupAnimal = self.source.TblAnimalGroupAnimal
        TblBmpAnimalGroup = self.source.TblBmpAnimalGroup
        TblBmp = self.source.TblBmp
        TblBmpType = self.source.TblBmpType
        TblAgency = self.source.TblAgency
        TblLoadSource = self.source.TblLoadSource
        TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource

        sca_table = SourceFromToAgencyIDtable.copy()

        # Baseconditionid is needed for indexing with the AnimalPopulation table, so and a column for it to the SCAtable
        sca_table.loc[:, 'baseconditionid'] = int(baseconditionid['baseconditionid'])

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

        # Get the BMPs that can be applied to each animalgroupid
        # !! Use the table assumption that animalgroupid is equal to animalid for each individual animal !!
        columnmask = ['animalgroupid', 'bmpid']
        tblsubset = TblBmpAnimalGroup.loc[:, columnmask].merge(tblsubset, how='right',
                                                               left_on='animalgroupid', right_on='animalid')
        tblsubset.drop(['animalgroupid'], axis=1, inplace=True)
        tblsubset.drop_duplicates(inplace=True)

        # Remove those bmps that aren't of type "Manure Transport"
        manuretypeid = TblBmpType['bmptypeid'][TblBmpType['bmptype'] == 'Manure Transport'].values[0]
        columnmask = ['bmpid', 'bmptypeid']
        tblsubset = TblBmp.loc[:, columnmask].merge(tblsubset, how='inner')
        tblsubset = tblsubset.loc[tblsubset['bmptypeid'] == manuretypeid]
        tblsubset.drop(['bmptypeid'], axis=1, inplace=True)

        # Convert loadsourceids to loadsourcegroupids
        columnmask = ['loadsourcegroupid', 'loadsourceid']
        tblsubset = TblLoadSourceGroupLoadSource.loc[:, columnmask].merge(tblsubset, how='inner')
        tblsubset.drop(['loadsourceid'], axis=1, inplace=True)

        return tblsubset

    def get_land_uplandbmps_to_exclude(self):
        # they are already affected when a land use change BMP is applied
        #  (This is based on an email conversation w/Jess on 8 May 2018
        #   [subject: "question: Efficiency parts of land use change BMPs"]
        #   and a convo w/Olivia on 2 May 2018 [subject: "quick followup"])
        TblBmp = self.source.TblBmp
        TblBmpScenarioType = self.source.TblBmpScenarioType

        subsetscenario1 = TblBmpScenarioType.loc[TblBmpScenarioType['scenariotypeid'] == 1]

        columnmask = ['bmpid', 'bmpshortname']
        tblsubset = TblBmp.loc[:, columnmask].merge(subsetscenario1, how='left', indicator=True)
        tblsubset = tblsubset[tblsubset['_merge'] == 'left_only']

        return tblsubset.loc[:, ['bmpid', 'bmpshortname']]

    def appendBmpSector_to_table_with_bmpid(self):
        pass

    def appendBmpType_to_table_with_bmpid(self, bmpidstable):
        TblBmp = self.source.TblBmp
        TblBmpType = self.source.TblBmpType

        columnmask = ['bmpid', 'bmptypeid']
        tblsubset = TblBmp.loc[:, columnmask].merge(bmpidstable, how='inner')

        columnmask = ['bmptypeid', 'bmptype']
        tblsubset = TblBmpType.loc[:, columnmask].merge(tblsubset, how='inner')

        tblsubset.drop(['bmptypeid'], axis=1, inplace=True)

        return tblsubset

    def appendBmpType_to_table_with_bmpshortnames(self, bmpshortnamestable):
        TblBmp = self.source.TblBmp

        bmpshortnamestable.rename(columns={'BmpShortname': 'bmpshortname'}, inplace=True)

        columnmask = ['bmpshortname', 'bmpid']
        tblsubset = TblBmp.loc[:, columnmask].merge(bmpshortnamestable, how='inner')

        tblsubset = self.appendBmpType_to_table_with_bmpid(tblsubset)
        tblsubset.drop(['bmpid'], axis=1, inplace=True)

        tblsubset.rename(columns={'bmpshortname': 'BmpShortname'}, inplace=True)

        return tblsubset

    def appendBmpGroup_to_table_with_bmpid(self):
        pass

    def append_unitids_to_table_with_bmpids(self, bmpidtable):
        TblBmpUnit = self.source.TblBmpUnit
        TblUnitRelation = self.source.TblUnitRelation
        TblUnit = self.source.TblUnit

        tblsubset = bmpidtable

        # Some bmp units are only optional.
        # Let's get their ids, and then exclude them
        urid = TblUnitRelation[TblUnitRelation['unitrelation'] == 'Supplemental Optional']['unitrelationid']
        RequiredRelations = TblUnitRelation[~TblUnitRelation['unitrelationid'].isin(list(urid))]
        columnmask = ['bmpid', 'unitid', 'unitrelationid', 'bmpunitfullname']
        BmpUnitsRequired = TblBmpUnit.loc[:, columnmask].merge(RequiredRelations, how='inner')

        # This is a helper function for the following code to filter by different units
        def filter_for_specificunit(grp, unitid):
            filtered = grp[grp['unitid'] == unitid]
            if filtered.empty:
                return grp
            else:
                return filtered

        # If a Bmp-unitrelationid group has 'percent' as one of the units, then we're going to drop the other units
        # Separate the parent units and the required supplemental units and keep 'percent' if it's there
        percentid = TblUnit[TblUnit['unit'] == 'percent']['unitid'].values[0]
        grouped = BmpUnitsRequired.groupby(['bmpid', 'unitrelationid'], as_index=False)
        groupedAfterPercentPrecedence = grouped.apply(lambda x: filter_for_specificunit(x, percentid))
        groupedAfterPercentPrecedence.head(10)
        bmpswithpercent = groupedAfterPercentPrecedence[groupedAfterPercentPrecedence['unitid'] == percentid]
        bmpswithoutpercent = groupedAfterPercentPrecedence[~(groupedAfterPercentPrecedence['unitid'] == percentid)]

        # After having checked 'percent', we'll check if 'acres' is one of the units and drop the others
        acresid = TblUnit[TblUnit['unit'] == 'acres']['unitid'].values[0]
        # Separate the parent units and the required supplemental units and keep 'percent' if it's there
        grouped = bmpswithoutpercent.groupby(['bmpid', 'unitrelationid'], as_index=False)
        groupedAfterAcresPrecedence = grouped.apply(lambda x: filter_for_specificunit(x, acresid))
        groupedAfterAcresPrecedence.head(10)
        bmpswithacres = groupedAfterAcresPrecedence[groupedAfterAcresPrecedence['unitid'] == acresid]
        bmpswithoutacres = groupedAfterAcresPrecedence[~(groupedAfterAcresPrecedence['unitid'] == acresid)]

        # After having checked 'percent' and 'acres', we'll check if 'feet' is one of the units and drop the others
        feetid = TblUnit[TblUnit['unit'] == 'feet']['unitid'].values[0]
        # Separate the parent units and the required supplemental units and keep 'percent' if it's there
        grouped = bmpswithoutacres.groupby(['bmpid', 'unitrelationid'], as_index=False)
        groupedAfterFeetPrecedence = grouped.apply(lambda x: filter_for_specificunit(x, feetid))
        groupedAfterFeetPrecedence.head(10)
        bmpswithfeet = groupedAfterFeetPrecedence[groupedAfterFeetPrecedence['unitid'] == feetid]
        bmpswithoutfeet = groupedAfterFeetPrecedence[~(groupedAfterFeetPrecedence['unitid'] == feetid)]

        # After having checked 'percent', 'acres', and 'feet',
        #   we'll check if 'dry tons' is one of the units and drop the others
        feetid = TblUnit[TblUnit['unit'] == 'wet tons']['unitid'].values[0]
        # Separate the parent units and the required supplemental units and keep 'percent' if it's there
        grouped = bmpswithoutacres.groupby(['bmpid', 'unitrelationid'], as_index=False)
        groupedAfterFeetPrecedence = grouped.apply(lambda x: filter_for_specificunit(x, feetid))
        groupedAfterFeetPrecedence.head(10)
        bmpswithfeet = groupedAfterFeetPrecedence[groupedAfterFeetPrecedence['unitid'] == feetid]
        bmpswithoutfeet = groupedAfterFeetPrecedence[~(groupedAfterFeetPrecedence['unitid'] == feetid)]

        # Get all the Bmps that have more than one required unit (^besides percent)
        bmpswithmultipleunitentries = groupedAfterFeetPrecedence[groupedAfterFeetPrecedence.duplicated(['bmpid'],
                                                                                                       keep=False)]

        FilteredBmpUnits = pd.concat([bmpswithpercent, bmpswithacres, bmpswithfeet, bmpswithoutfeet]).sort_values(by=['bmpid'])

        # Check to make sure:
        # there shoudn't be any rows with duplicate bmpids if they don't have
        #   a required supplemental unit (unitrelationid==2)
        checktbl = FilteredBmpUnits[FilteredBmpUnits.duplicated(['bmpid'], keep=False)].copy()
        # Add column with frequency of each unitrelationid for each bmpid.
        checktbl['howmany'] = checktbl.groupby(['bmpid', 'unitrelationid'])['unitrelationid'].transform('count')
        uhoh = checktbl[(checktbl['unitrelationid'] == 1) & (checktbl['howmany'] > 1)]
        if not uhoh.empty:
            raise ValueError("there shouldn't be any duplicate required units")

        columnmask = ['bmpid', 'unitid', 'unitrelationid', 'bmpunitfullname']
        newtable = FilteredBmpUnits.loc[:, columnmask].merge(tblsubset, how='inner')

        return newtable
