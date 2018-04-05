import os
import pickle
import numpy as np
import pandas as pd
from itertools import product
from tqdm import tqdm

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


class TblJeeves:
    def __init__(self):
        """Wrapper for table queries. Provides methods for querying different information

        Attributes:
            source (SourceData): The source object contains all of the data tables

        """
        self.source = self.loadSourceFromSQL()

    def loadSourceFromSQL(self):
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

    def lrsegids_from(self, lrsegnames=None, countystatestrs=None, countyid=None):
        kwargs = (lrsegnames, countystatestrs, countyid)
        if checkOnlyOne(kwargs) is False:
            raise ValueError('One and only one keyword argument must be specified')

        if lrsegnames is not None:
            return self.__lrsegids_from_lrsegnames(getfrom=lrsegnames)
        elif countystatestrs is not None:
            return self.__lrsegids_from_countystatestrs(getfrom=countystatestrs)
        elif countyid is not None:
            return self.__lrsegids_from_countyid(getfrom=countyid)

    def __lrsegids_from_lrsegnames(self, getfrom=None):
        if isinstance(getfrom, list):
            getfrom = pd.DataFrame(getfrom, columns=['landriversegment'])

        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data
        columnmask = ['lrsegid', 'landriversegment']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(getfrom, how='inner')

        return tblsubset.loc[:, ['lrsegid']]  # pass column name as list so return type is pandas.DataFrame

    def __lrsegids_from_countystatestrs(self, getfrom=None):
        countyids = self.countyid_from_countystatestrs(getfrom=getfrom)
        return self.__lrsegids_from_countyid(getfrom=countyids)

    def __lrsegids_from_countyid(self, getfrom=None):
        if isinstance(getfrom, list):
            getfrom = pd.DataFrame(getfrom, columns=['countyid'])

        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data

        columnmask = ['lrsegid', 'landriversegment', 'stateid', 'countyid', 'outofcbws']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(getfrom, how='inner')

        return tblsubset.loc[:, ['lrsegid']]  # pass column name as list so return type is pandas.DataFrame

    def countyid_from_countystatestrs(self, getfrom=None):
        TblCounty = self.source.TblCounty  # get relevant source data

        areas = [x.split(', ') for x in getfrom]  # split ('County, StateAbbrev')
        rowmask = pd.DataFrame(areas, columns=['countyname', 'stateabbreviation'])

        columnmask = ['countyid', 'countyname', 'stateid', 'stateabbreviation', 'fips']
        tblsubset = TblCounty.loc[:, columnmask].merge(rowmask, how='inner')

        return tblsubset.loc[:, ['countyid']]  # pass column name as list so return type is pandas.DataFrame

    def lrsegs_from_geography(self, scale='', areanames=None):
        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data
        if scale == 'County':
            getfrom = self.lrsegids_from(countystatestrs=areanames)
            columnmask = ['lrsegid', 'landriversegment']
            tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(getfrom, how='inner')
            return tblsubset.loc[:, ['landriversegment']]

    def agencyids_from(self, agencycodes=None):
        if isinstance(agencycodes, list):
            agencycodes = pd.DataFrame(agencycodes, columns=['agencycode'])

        TblAgency = self.source.TblAgency  # get relevant source data
        columnmask = ['agencycode', 'agencyid']
        tblsubset = TblAgency.loc[:, columnmask].merge(agencycodes, how='inner')

        return tblsubset.loc[:, ['agencyid']]

    def agencies_from_lrsegs(self, lrsegnames=None):
        if not isinstance(lrsegnames, list):
            lrsegnames = lrsegnames.tolist()

        TblAgency = self.source.TblAgency  # get relevant source data
        TblLandRiverSegmentAgency = self.source.TblLandRiverSegmentAgency

        tblwithlrsegids = self.lrsegids_from(lrsegnames=lrsegnames)

        columnmask = ['lrsegid', 'agencyid', 'acres']
        tblwithagencyids = TblLandRiverSegmentAgency.loc[:, columnmask].merge(tblwithlrsegids, how='inner')

        columnmask = ['agencyid', 'agencycode', 'agencyfullname', 'agencytypeid']
        tblsubset = TblAgency.loc[:, columnmask].merge(tblwithagencyids, how='inner')

        return tblsubset.loc[:, ['agencycode']]

    def all_agency_names(self):
        TblAgency = self.source.TblAgency  # get relevant source data
        return TblAgency.loc[:, 'agencycode']

    def sectorids_from(self, sectornames=None):
        if isinstance(sectornames, list):
            sectornames = pd.DataFrame(sectornames, columns=['sector'])

        TblSector = self.source.TblSector  # get relevant source data
        columnmask = ['sector', 'sectorid']
        tblsubset = TblSector.loc[:, columnmask].merge(sectornames, how='inner')

        return tblsubset.loc[:, ['sectorid']]

    def all_sector_names(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, 'sector']

    def all_geotypes(self):
        TblGeoType = self.source.TblGeographyType  # get relevant source data
        TblGeoType = TblGeoType.loc[TblGeoType['castscenariogeographytype'] == True]
        return TblGeoType.loc[:, ['geographytypeid', 'geographytype']]

    def all_geonames_of_geotype(self, geotype=None):
        TblGeography = self.source.TblGeography  # get relevant source data
        if not geotype:
            raise ValueError('Geography Type must be specified to get area names')

        if isinstance(geotype, list):
            if isinstance(geotype[0], str):
                # Assume that if string, then we have been passed a geographytypename instead of a geographytypeid
                TblGeoType = self.source.TblGeographyType  # get relevant source data
                typenames = pd.DataFrame(geotype, columns=['geographytype'])
                columnmask = ['geographytypeid', 'geographytype']
                typeids = TblGeoType.loc[:, columnmask].merge(typenames, how='inner')
            else:
                typeids = pd.DataFrame(geotype, columns=['geographytypeid'])
        elif isinstance(geotype, pd.DataFrame):
            typeids = geotype
            pass
        else:
            raise ValueError('Geography Type must be specified as a list of str, list of ids, or pandas.DataFrame')

        if len(typeids) == 0:
            raise ValueError('Geography Type %s was unrecognized' % geotype)

        columnmask = ['geographyid', 'geographytypeid', 'geographyfullname']
        tblsubset = TblGeography.loc[:, columnmask].merge(typeids, how='inner')
        return tblsubset.loc[:, 'geographyfullname']

    def loadsourcegroupids_from(self, sectorids=None):
        if isinstance(sectorids, list):
            sectorids = pd.DataFrame(sectorids, columns=['sectorid'])

        TblLoadSourceGroupSector = self.source.TblLoadSourceGroupSector  # get relevant source data
        columnmask = ['loadsourcegroupid', 'sectorid']
        tblsubset = TblLoadSourceGroupSector.loc[:, columnmask].merge(sectorids, how='inner')

        return tblsubset.loc[:, ['loadsourcegroupid']]

    def loadsources_from_lrseg_agency_sector(self, lrsegs=None, agencies=None, sectors=None):
        """Get the load sources present (whether zero acres or not) in the specified lrseg-agency-sectors
        """
        # get relevant source data
        TblLandUsePreBmp = self.source.TblLandUsePreBmp  # use this to find load sources with >0 acres
        TblLandRiverSegmentAgencyLoadSource = self.source.TblLandRiverSegmentAgencyLoadSource
        TblLoadSource = self.source.TblLoadSource
        TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource

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
        loadsourcegroupids = self.loadsourcegroupids_from(sectorids=sectorids)
        columnmask = ['loadsourcegroupid', 'loadsourceid']
        tblloadsourceids2 = TblLoadSourceGroupLoadSource.loc[:, columnmask].merge(loadsourcegroupids, how='inner')

        # get the intersection of these two loadsourceid tables
        tblloadsourceids = tblloadsourceids1.merge(tblloadsourceids2, how='inner')

        # get the loadsource names from their ids
        columnmask = ['loadsourceid', 'loadsource']
        tblsubset = TblLoadSource.loc[:, columnmask].merge(tblloadsourceids, how='inner')

        return tblsubset.loc[:, ['loadsource']]
