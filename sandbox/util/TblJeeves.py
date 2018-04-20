import os
import pickle
import numpy as np
import pandas as pd
from itertools import product
from itertools import permutations
from tqdm import tqdm
import warnings

from sandbox.sqltables.source_data import SourceData
from sandbox.__init__ import get_tempdir
from sandbox.__init__ import get_sqlsourcetabledir


def loadDataframe(tblName, loc):
    dtype_dict = {}
    if tblName == "ImpBmpSubmittedManureTransport":
        dtype_dict["fipsfrom"] = np.str

    fileLocation = os.path.join(loc, tblName + ".csv")

    df = pd.read_csv(fileLocation, dtype=dtype_dict, encoding="utf-8")

    # Added by DEKAUFMAN to read csv in chunks instead of all at once
    #tp = pd.read_csv(fileLocation, header=None, encoding="utf-8", chunksize=500000)
    #df = pd.concat(tp, ignore_index=True)

    df = df.rename(columns={column: column.lower() for column in df.columns})

    if tblName == "TblBmpGroup":
        df["ruleset"] = df["ruleset"].astype(str).str.lower()
    return df


def checkOnlyOne(iterable):
    i = iter(iterable)
    return any(i) and not any(i)


def forceToSingleColumnDataFrame(inputarg, colname=''):
    if not isinstance(inputarg, pd.DataFrame):
        return pd.DataFrame(inputarg, columns=[colname])
    else:
        return inputarg


class TblJeeves:
    def __init__(self):
        """Wrapper for table queries. Provides methods for querying different information

        Attributes:
            source (SourceData): The source object contains all of the data tables

        """
        self.source = self.loadInSourceDataFromSQL()

    def loadInSourceDataFromSQL(self):
        savename = get_tempdir() + 'SourceData.obj'

        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                sourcedata = pickle.load(f)
        else:
            print('<%s object does not exist yet. Generating...>' % SourceData.__name__)
            # Source tables are loaded.
            sourcedata = SourceData()
            tbllist = sourcedata.getTblList()
            for tblName in tqdm(tbllist, total=len(tbllist)):
                # for tblName in tbllist:
                # print("loading source:", tblName)
                df = loadDataframe(tblName, get_sqlsourcetabledir())
                sourcedata.addTable(tblName, df)

            with open(savename, 'wb') as f:
                pickle.dump(sourcedata, f)

        return sourcedata

    # Methods to get metadata options
    def base_year_names(self):
        return ['640', '1642', '1812', '1918']

    def base_condition_names(self):
        return ['BaseCondition0001', 'BaseCondition0002', 'BaseCondition0003', 'BaseCondition0004']

    def wastewaterdata_names(self):
        return ['WasteWater0001', 'WasteWater0002', 'WasteWater0003', 'WasteWater0004']

    def costprofile_names(self):
        return ['CostProfile0001', 'CostProfile0002', 'CostProfile0003', 'CostProfile0004']

    # Geography Methods
    def all_geotypes(self):
        TblGeoType = self.source.TblGeographyType  # get relevant source data
        TblGeoType = TblGeoType.loc[TblGeoType['castscenariogeographytype'] == True]
        return TblGeoType.loc[:, ['geographytypeid', 'geographytype', 'geographytypefullname']]

    def geonames_from_geotypeid(self, geotype=None):
        TblGeography = self.source.TblGeography  # get relevant source data
        if not geotype:
            raise ValueError('Geography Type must be specified to get area names')

        if isinstance(geotype, list):
            if isinstance(geotype[0], str):
                # Assume that if string, then we have been passed a geographytypename instead of a geographytypeid
                raise ValueError('If using a geotypename, then use the geonames_from_geotypename() method')
            else:
                typeids = pd.DataFrame(geotype, columns=['geographytypeid'])
        elif isinstance(geotype, pd.DataFrame):
            typeids = geotype
        else:
            raise ValueError('Geography Type must be specified as a list of str, list of ids, or pandas.DataFrame')

        if len(typeids) == 0:
            raise ValueError('Geography Type %s was unrecognized' % geotype)

        columnmask = ['geographyid', 'geographytypeid', 'geographyfullname']
        tblsubset = TblGeography.loc[:, columnmask].merge(typeids, how='inner')
        return tblsubset.loc[:, 'geographyfullname']

    def geonames_from_geotypename(self, geotype=None):
        TblGeography = self.source.TblGeography  # get relevant source data
        TblGeographyType = self.source.TblGeographyType

        if not geotype:
            raise ValueError('Geography Type must be specified to get area names')

        if isinstance(geotype, list):
            typenames = pd.DataFrame(geotype, columns=['geographytypefullname'])
        elif isinstance(geotype, pd.DataFrame):
            typenames = geotype
        elif isinstance(geotype, str):
            typenames = pd.DataFrame([geotype], columns=['geographytypefullname'])
            if geotype == 'Select Geographic Scale':
                return []
        else:
            raise ValueError('Geography Type must be specified as a list of str, list of ids, or pandas.DataFrame')

        columnmask = ['geographytypeid', 'geographytypefullname']
        typeids = TblGeographyType.loc[:, columnmask].merge(typenames, how='inner')

        if len(typeids) == 0:
            raise ValueError('Geography Type %s was unrecognized' % geotype)

        columnmask = ['geographytypeid', 'geographyfullname']
        tblsubset = TblGeography.loc[:, columnmask].merge(typeids, how='inner')
        return tblsubset.loc[:, 'geographyfullname']

    def countyid_from_countystatestrs(self, getfrom=None):
        TblCounty = self.source.TblCounty  # get relevant source data

        areas = [x.split(', ') for x in getfrom]  # split ('County, StateAbbrev')
        rowmask = pd.DataFrame(areas, columns=['countyname', 'stateabbreviation'])

        columnmask = ['countyid', 'countyname', 'stateid', 'stateabbreviation', 'fips']
        tblsubset = TblCounty.loc[:, columnmask].merge(rowmask, how='inner')

        return tblsubset.loc[:, ['countyid']]  # pass column name as list so return type is pandas.DataFrame

    def lrsegnames_from(self, lrsegids=None):
        lrsegids = forceToSingleColumnDataFrame(lrsegids, colname='landriversegment')

        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data
        columnmask = ['lrsegid', 'landriversegment']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(lrsegids, how='inner')

        return tblsubset.loc[:, ['landriversegment']]  # pass column name as list so return type is pandas.DataFrame

    def lrsegids_from(self, lrsegnames=None, countystatestrs=None, countyid=None):
        kwargs = (lrsegnames, countystatestrs, countyid)
        kwargsNoDataFrames = [True if isinstance(x, pd.DataFrame) else x for x in kwargs]
        if checkOnlyOne(kwargsNoDataFrames) is False:
            raise ValueError('One and only one keyword argument must be specified')

        if lrsegnames is not None:
            return self.__lrsegids_from_lrsegnames(getfrom=lrsegnames)
        elif countystatestrs is not None:
            return self.__lrsegids_from_countystatestrs(getfrom=countystatestrs)
        elif countyid is not None:
            return self.__lrsegids_from_countyid(getfrom=countyid)
        else:
            raise ValueError('unrecognized input')

    def __lrsegids_from_lrsegnames(self, getfrom=None):
        getfrom = forceToSingleColumnDataFrame(getfrom, colname='landriversegment')

        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data
        columnmask = ['lrsegid', 'landriversegment']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(getfrom, how='inner')

        return tblsubset.loc[:, ['lrsegid']]  # pass column name as list so return type is pandas.DataFrame

    def __lrsegids_from_countystatestrs(self, getfrom=None):
        countyids = self.countyid_from_countystatestrs(getfrom=getfrom)
        return self.__lrsegids_from_countyid(getfrom=countyids)

    def __lrsegids_from_countyid(self, getfrom=None):
        getfrom = forceToSingleColumnDataFrame(getfrom, colname='countyid')

        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data

        columnmask = ['lrsegid', 'landriversegment', 'stateid', 'countyid', 'outofcbws']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(getfrom, how='inner')

        return tblsubset.loc[:, ['lrsegid']]  # pass column name as list so return type is pandas.DataFrame

    def lrsegids_from_geoscale_with_names(self, scale='', areanames=None):
        if scale == 'County':
            tblsubset = self.lrsegids_from(countystatestrs=areanames)
            return tblsubset.loc[:, ['lrsegid']]
        else:
            warnings.warn('Specified scale "%s" is unrecognized' % scale, RuntimeWarning)
            return None

    def countyids_from_lrsegids(self, lrsegids=None):
        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data
        columnmask = ['lrsegid', 'countyid']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(lrsegids, how='inner')

        return tblsubset.loc[:, ['countyid']]  # pass column name as list so return type is pandas.DataFrame

    # Agency Methods
    def agencyids_from(self, agencycodes=None):
        agencycodes = forceToSingleColumnDataFrame(agencycodes, colname='agencycode')

        TblAgency = self.source.TblAgency  # get relevant source data
        columnmask = ['agencycode', 'agencyid']
        tblsubset = TblAgency.loc[:, columnmask].merge(agencycodes, how='inner')

        return tblsubset.loc[:, ['agencyid']]

    def agencylrsegidtable_from_lrsegids(self, lrsegids=None):
        TblLandRiverSegmentAgency = self.source.TblLandRiverSegmentAgency  # get relevant source data

        columnmask = ['lrsegid', 'agencyid']
        tblsubset = TblLandRiverSegmentAgency.loc[:, columnmask].merge(lrsegids, how='inner')

        return tblsubset.loc[:, ['lrsegid', 'agencyid']]

    def agencies_from_lrsegnames(self, lrsegnames=None):
        if not isinstance(lrsegnames, list):
            lrsegnames = lrsegnames.tolist()

        TblAgency = self.source.TblAgency  # get relevant source data

        tblwithlrsegids = self.lrsegids_from(lrsegnames=lrsegnames)
        tblwithagencyids = self.agencylrsegidtable_from_lrsegids(lrsegids=tblwithlrsegids).loc[:, ['agencyid']]

        columnmask = ['agencyid', 'agencycode', 'agencyfullname', 'agencytypeid']
        tblsubset = TblAgency.loc[:, columnmask].merge(tblwithagencyids, how='inner')

        return tblsubset.loc[:, ['agencycode']]

    def agencies_from_lrsegids(self, lrsegids=None):
        TblAgency = self.source.TblAgency  # get relevant source data

        tblwithagencyids = self.agencylrsegidtable_from_lrsegids(lrsegids=lrsegids).loc[:, ['agencyid']]

        columnmask = ['agencyid', 'agencycode', 'agencyfullname', 'agencytypeid']
        tblsubset = TblAgency.loc[:, columnmask].merge(tblwithagencyids, how='inner')

        return tblsubset.loc[:, ['agencycode']]

    def all_agency_names(self):
        TblAgency = self.source.TblAgency  # get relevant source data
        return TblAgency.loc[:, 'agencycode']

    # Sector Methods
    def sectorids_from(self, sectornames=None):
        sectornames = forceToSingleColumnDataFrame(sectornames, colname='sector')

        TblSector = self.source.TblSector  # get relevant source data
        columnmask = ['sector', 'sectorid']
        tblsubset = TblSector.loc[:, columnmask].merge(sectornames, how='inner')

        return tblsubset.loc[:, ['sectorid']]

    def all_sector_names(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, 'sector']

    def all_sectorids(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, ['sectorid']]

    # Load Source Methods
    def loadsourcegroupids_from(self, sectorids=None, loadsourceids=None):

        kwargs = (sectorids, loadsourceids)
        kwargsNoDataFrames = [True if isinstance(x, pd.DataFrame) else x for x in kwargs]
        if checkOnlyOne(kwargsNoDataFrames) is False:
            raise ValueError('One and only one keyword argument must be specified')

        if sectorids is not None:
            sectorids = forceToSingleColumnDataFrame(sectorids, colname='sectorid')

            TblLoadSourceGroupSector = self.source.TblLoadSourceGroupSector  # get relevant source data
            columnmask = ['loadsourcegroupid', 'sectorid']
            tblsubset = TblLoadSourceGroupSector.loc[:, columnmask].merge(sectorids, how='inner')
        elif loadsourceids is not None:
            loadsourceids = forceToSingleColumnDataFrame(loadsourceids, colname='loadsourceid')

            TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource  # get relevant source data
            columnmask = ['loadsourcegroupid', 'loadsourceid']
            tblsubset = TblLoadSourceGroupLoadSource.loc[:, columnmask].merge(loadsourceids, how='inner')
        else:
            tblsubset = None
            raise ValueError('unrecognized input')

        return tblsubset.loc[:, ['loadsourcegroupid']]

    def loadsourceids_from(self, sectorids=None):
        sectorids = forceToSingleColumnDataFrame(sectorids, colname='sectorid')

        TblLoadSource = self.source.TblLoadSource  # get relevant source data
        columnmask = ['loadsourceid', 'sectorid']
        tblsubset = TblLoadSource.loc[:, columnmask].merge(sectorids, how='inner')

        return tblsubset.loc[:, ['loadsourceid']]

    def sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(self, lrsegagencyidtable=None, sectorids=None):
        """Get the load sources present (whether zero acres or not) in the specified lrseg-agency-sectors
        """
        # get relevant source data
        TblLandRiverSegmentAgencyLoadSource = self.source.TblLandRiverSegmentAgencyLoadSource

        # use [lrseg, agency] to get loadsourceids
        columnmask = ['lrsegid', 'agencyid', 'loadsourceid', 'unitid']
        tblloadsourceids1 = TblLandRiverSegmentAgencyLoadSource.loc[:, columnmask].merge(lrsegagencyidtable,
                                                                                         how='inner')

        # use sectors/loadsourcegroups to get loadsourceids
        tblloadsourceids2 = self.loadsourceids_from(sectorids=sectorids)

        # get the intersection of these two loadsourceid tables
        tblsubset = tblloadsourceids1.merge(tblloadsourceids2, how='inner')

        return tblsubset

    def sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(self, sourceAgencyLrsegIDtable=None):
        # get relevant source data
        TblLandRiverSegment = self.source.TblLandRiverSegment

        columnmask = ['lrsegid', 'countyid']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(sourceAgencyLrsegIDtable, how='inner')

        tblsubset.drop_duplicates(subset=['countyid', 'agencyid', 'loadsourceid'], inplace=True)

        return tblsubset.loc[:, ['countyid', 'agencyid', 'loadsourceid']]

    def loadsourceids_from_lrsegid_agencyid_sectorid(self, lrsegids=None, agencyids=None, sectorids=None):
        """Get the load sources present (whether zero acres or not) in the specified lrseg-agency-sectors
        """
        # get relevant source data
        TblLandRiverSegmentAgencyLoadSource = self.source.TblLandRiverSegmentAgencyLoadSource

        # Generate all combinations of the lrseg, agency, sectors
        combos = list(product(lrsegids['lrsegid'], agencyids['agencyid']))
        combos = pd.DataFrame(combos, columns=['lrsegid', 'agencyid'])

        # use [lrseg, agency] to get loadsourceids
        columnmask = ['lrsegid', 'agencyid', 'loadsourceid', 'unitid']
        tblloadsourceids1 = TblLandRiverSegmentAgencyLoadSource.loc[:, columnmask].merge(combos, how='inner')

        # use sectors/loadsourcegroups to get loadsourceids
        tblloadsourceids2 = self.loadsourceids_from(sectorids=sectorids)

        # get the intersection of these two loadsourceid tables
        tblloadsourceids = tblloadsourceids1.merge(tblloadsourceids2, how='inner')

        return tblloadsourceids.loc[:, ['loadsourceid']]

    def loadsources_from_lrseg_agency_sector(self, lrsegs=None, agencies=None, sectors=None):
        """Get the load sources present (whether zero acres or not) in the specified lrseg-agency-sectors
        """
        # get relevant source data
        TblLandUsePreBmp = self.source.TblLandUsePreBmp  # use this to find load sources with >0 acres
        TblLandRiverSegmentAgencyLoadSource = self.source.TblLandRiverSegmentAgencyLoadSource
        TblLoadSource = self.source.TblLoadSource
        TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource

        # Convert names to IDs
        lrsegids = self.lrsegids_from(lrsegnames=lrsegs)
        agencyids = self.agencyids_from(agencycodes=agencies)
        sectorids = self.sectorids_from(sectornames=sectors)

        # Generate all combinations of the lrseg, agency, sectors
        combos = list(product(lrsegids['lrsegid'], agencyids['agencyid']))
        combos = pd.DataFrame(combos, columns=['lrsegid', 'agencyid'])

        # use [lrseg, agency] to get loadsourceids
        columnmask = ['lrsegid', 'agencyid', 'loadsourceid', 'unitid']
        tblloadsourceids1 = TblLandRiverSegmentAgencyLoadSource.loc[:, columnmask].merge(combos, how='inner')

        # use sectors/loadsourcegroups to get loadsourceids
        tblloadsourceids2 = self.loadsourceids_from(sectorids=sectorids)

        # get the intersection of these two loadsourceid tables
        tblloadsourceids = tblloadsourceids1.merge(tblloadsourceids2, how='inner')

        # get the loadsource names from their ids
        columnmask = ['loadsourceid', 'loadsource']
        tblsubset = TblLoadSource.loc[:, columnmask].merge(tblloadsourceids, how='inner')

        return tblsubset.loc[:, ['loadsource']]

    # BMP Methods
    def all_bmpnames(self):
        TblBmp = self.source.TblBmp  # get relevant source data]
        return TblBmp.loc[:, 'bmpshortname']

    def single_bmpid_from_shortname(self, bmpshortname):
        TblBmp = self.source.TblBmp  # get relevant source data
        return TblBmp['bmpid'][TblBmp['bmpshortname'] == bmpshortname].tolist()

    def bmpids_from_categoryids(self, categoryids):
        categoryids = forceToSingleColumnDataFrame(categoryids, colname='bmpcategoryid')

        TblBmp = self.source.TblBmp  # get relevant source data
        columnmask = ['bmpcategoryid', 'bmpid']
        tblsubset = TblBmp.loc[:, columnmask].merge(categoryids, how='inner')

        return tblsubset.loc[:, ['bmpid']]

    def bmpnames_from_bmpids(self, bmpids):
        bmpids = forceToSingleColumnDataFrame(bmpids, colname='bmpid')

        TblBmp = self.source.TblBmp  # get relevant source data
        columnmask = ['bmpshortname', 'bmpid']
        tblsubset = TblBmp.loc[:, columnmask].merge(bmpids, how='inner')

        return tblsubset.loc[:, ['bmpshortname']]

    def land_slabidtable_from_SourceLrsegAgencyIDtable(self, SourceLrsegAgencyIDtable):
        TblBmpLoadSourceFromTo = self.source.TblBmpLoadSourceFromTo

        TblBmpLoadSourceFromTo.rename(columns={'fromloadsourceid': 'loadsourceid'}, inplace=True)
        columnmask = ['bmpid', 'loadsourceid']
        tblsubset = TblBmpLoadSourceFromTo.loc[:, columnmask].merge(SourceLrsegAgencyIDtable, how='inner')

        return tblsubset

    def animal_scabidtable_from_SourceCountyAgencyIDtable(self, SourceCountyAgencyIDtable, baseconditionid=None):
        TblAnimalPopulation = self.source.TblAnimalPopulation
        TblAnimalGroupAnimal = self.source.TblAnimalGroupAnimal
        TblBmpAnimalGroup = self.source.TblBmpAnimalGroup
        TblAgency = self.source.TblAgency

        sca_table = SourceCountyAgencyIDtable.copy()

        # For Animals, only the NONFED agency matters, so remove all rows with agencies not equal to NONFED
        nonfedid = TblAgency['agencyid'][TblAgency['agencycode'] == 'NONFED'].values[0]
        sca_table = sca_table[sca_table["agencyid"] == nonfedid]

        # Baseconditionid is needed for indexing with the AnimalPopulation table, so and a column for it to the SCAtable
        sca_table['baseconditionid'] = baseconditionid.baseconditionid.tolist()[0]

        # Get which animals are present in the county, agency, loadsources
        columnmask = ['baseconditionid', 'countyid', 'loadsourceid', 'animalid', 'animalcount', 'animalunits']
        tblsubset = TblAnimalPopulation.loc[:, columnmask].merge(sca_table, how='inner')

        # Get the animalgroups that each animalid belongs to
        columnmask = ['animalgroupid', 'animalid']
        tblsubset = TblAnimalGroupAnimal.loc[:, columnmask].merge(tblsubset, how='inner')

        # Get the BMPs that can be applied to each animalgroupid
        columnmask = ['animalgroupid', 'bmpid']
        tblsubset = TblBmpAnimalGroup.loc[:, columnmask].merge(tblsubset, how='inner')

        return tblsubset

    def manure_sftabidtable_from_SourceFromToAgencyIDtable(self, SourceCountyAgencyIDtable, baseconditionid=None):
        TblAnimalPopulation = self.source.TblAnimalPopulation
        TblAnimalGroupAnimal = self.source.TblAnimalGroupAnimal
        TblBmpAnimalGroup = self.source.TblBmpAnimalGroup
        TblBmp = self.source.TblBmp
        TblAgency = self.source.TblAgency
        TblLoadSource = self.source.TblLoadSource

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

        # Get the animalgroups that each animalid belongs to
        columnmask = ['animalgroupid', 'animalid']
        tblsubset = TblAnimalGroupAnimal.loc[:, columnmask].merge(tblsubset, how='inner')

        # # Get the BMPs that can be applied to each animalgroupid
        # columnmask = ['animalgroupid', 'bmpid']
        # tblsubset = TblBmpAnimalGroup.loc[:, columnmask].merge(tblsubset, how='inner')

        # For Manure transport, there's only one bmp that should be applied (?) TODO: check that this is true
        mtid = TblBmp['bmpid'][TblBmp['bmpshortname'] == 'ManureTransport'].values[0]
        tblsubset['bmpid'] = mtid

        tblsubset.drop(['countyid'], axis=1, inplace=True)

        return tblsubset

    # Hard Upper/Lower Bounds Methods
    def appendBounds_to_land_slabidtable(self, slabidtable=None):
        slabidtable['lowerbound'] = 0
        slabidtable['upperbound'] = 100
        # For Acres: Add all of the acres (across LoadSources) from "TblLandUsePreBmp"
        return slabidtable.copy()

    def appendBounds_to_animal_scabidtable(self, scabidtable=None):
        scabidtable['lowerbound'] = 0
        scabidtable['upperbound'] = 100
        # For Animals: Add...?
        return scabidtable.copy()

    def appendBounds_to_manure_sftabidtable(self, sftabidtable=None):
        sftabidtable['lowerbound'] = 0
        sftabidtable['upperbound'] = 100
        # For Dry_Tons_of_Stored_Manure: Add...?
        return sftabidtable.copy()

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

        # Translate countyid to GeographyName (FIPS) and add stateabbreviation
        columnmask = ['countyid', 'stateabbreviation', 'fips']
        newtable = TblCounty.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to Agency codes
        columnmask = ['agencycode', 'agencyid']
        newtable = TblAgency.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to LoadSource names
        columnmask = ['loadsource', 'loadsourceid']
        newtable = TblLoadSource.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to BMP names
        columnmask = ['bmpshortname', 'bmpid']
        newtable = TblBmp.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to AnimalGroup names
        columnmask = ['animalgroupid', 'animalgroup']
        newtable = TblAnimalGroup.loc[:, columnmask].merge(newtable, how='inner')

        newtable.drop(['countyid', 'agencyid', 'loadsourceid', 'bmpid',
                       'animalgroupid', 'animalid', 'baseconditionid'], axis=1, inplace=True)
        newtable.rename(columns={'fips': 'GeographyName',
                                 'stateabbreviation': 'StateAbbreviation',
                                 'agencycode': 'AgencyCode',
                                 'loadsource': 'LoadSourceGroup',
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
        # Translate to LoadSource names
        columnmask = ['loadsource', 'loadsourceid']
        newtable = TblLoadSource.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to BMP names
        columnmask = ['bmpshortname', 'bmpid']
        newtable = TblBmp.loc[:, columnmask].merge(newtable, how='inner')
        # Translate to AnimalGroup names
        columnmask = ['animalgroupid', 'animalgroup']
        newtable = TblAnimalGroup.loc[:, columnmask].merge(newtable, how='inner')

        newtable.drop(['agencyid', 'loadsourceid', 'bmpid',
                       'animalgroupid', 'animalid', 'baseconditionid'], axis=1, inplace=True)
        newtable.rename(columns={'stateabbreviation': 'StateAbbreviation',
                                 'agencycode': 'AgencyCode',
                                 'loadsource': 'LoadSourceGroup',
                                 'bmpshortname': 'BmpShortname',
                                 'animalgroup': 'AnimalGroup'}, inplace=True)

        newtable['Unit'] = 'Percent'

        if 'Amount' in newtable.columns:
            newtable['StateUniqueIdentifier'] = np.nan
            # Reorder columns to match CAST input table format
            newtable = newtable[['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                 'FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup', 'Amount', 'Unit']]

        return newtable

    def make_scenario_from_slabidtable(self, slabidtable=None):
        newtable = slabidtable

        newtable['stateuniqueidentifier'] = np.nan
        newtable['unitid'] = 1

        return newtable

    # Extra Info Methods
    def appendBmpSector_to_table_with_bmpid(self):
        pass

    def appendBmpType_to_table_with_bmpid(self):
        pass

    def appendBmpGroup_to_table_with_bmpid(self):
        pass

    def appendLoadSourceSector_to_table_with_loadsourceid(self):
        pass

    def appendLoadSourceMajor_to_table_with_loadsourceid(self):
        pass
