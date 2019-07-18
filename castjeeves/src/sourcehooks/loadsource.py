import pandas as pd
from itertools import product

from .sourcehooks import SourceHook
from .agency import Agency
from .lrseg import Lrseg
from .sector import Sector


class LoadSource(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Load Source Methods """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        self.agency = Agency(sourcedata=sourcedata, metadata=metadata)
        self.lrseg = Lrseg(sourcedata=sourcedata, metadata=metadata)
        self.sector = Sector(sourcedata=sourcedata, metadata=metadata)

    def all_names(self, astype=pd.Series):
        TblLoadSource = self.source.TblLoadSource  # get relevant source data]
        name_series = TblLoadSource.loc[:, 'loadsourceshortname']
        return self.type_convert(name_series, astype)

    def ids_from_names(self, names=None):
        return self._map_using_sourcetbl(names, tbl='TblLoadSource',
                                         fromcol='loadsourceshortname', tocol='loadsourceid')

    def names_from_ids(self, ids=None):
        return self._map_using_sourcetbl(ids, tbl='TblLoadSource',
                                         fromcol='loadsourceid', tocol='loadsourceshortname')

    def loadsourcegroupids_from(self, sectorids=None, loadsourceids=None):
        kwargs = (sectorids, loadsourceids)
        kwargsNoDataFrames = [True if isinstance(x, pd.DataFrame) else x for x in kwargs]
        if self.checkOnlyOne(kwargsNoDataFrames) is False:
            raise ValueError('One and only one keyword argument must be specified')

        if sectorids is not None:
            return self.__loadsourcegroupids_from_sectorids(getfrom=sectorids)
        elif loadsourceids is not None:
            return self.__loadsourcegroupids_from_loadsourceids(getfrom=loadsourceids)

    def __loadsourcegroupids_from_sectorids(self, getfrom=None):
        getfrom = self.forceToSingleColumnDataFrame(getfrom, colname='sectorid')
        return self.singleconvert(sourcetbl='TblLoadSourceGroupSector',
                                    toandfromheaders=['loadsourcegroupid', 'sectorid'],
                                    fromtable=getfrom, toname='loadsourcegroupid')

    def __loadsourcegroupids_from_loadsourceids(self, getfrom=None):
        getfrom = self.forceToSingleColumnDataFrame(getfrom, colname='loadsourceid')
        return self.singleconvert(sourcetbl='TblLoadSourceGroupLoadSource',
                                    toandfromheaders=['loadsourcegroupid', 'loadsourceid'],
                                    fromtable=getfrom, toname='loadsourcegroupid')

    def fullnames_from_shortnames(self, loadsourceshortname, use_order_of_sourcetbl=True):
        loadsourceshortname = self.forceToSingleColumnDataFrame(loadsourceshortname, colname='loadsourceshortname')
        return self.singleconvert(sourcetbl='TblLoadSource', toandfromheaders=['loadsource', 'loadsourceshortname'],
                                  fromtable=loadsourceshortname, toname='loadsource',
                                  use_order_of_sourcetbl=use_order_of_sourcetbl)

    def shortnames_from_fullnames(self, loadsourcefullname, use_order_of_sourcetbl=True):
        loadsource = self.forceToSingleColumnDataFrame(loadsourcefullname, colname='loadsource')
        return self.singleconvert(sourcetbl='TblLoadSource', toandfromheaders=['loadsourceshortname', 'loadsource'],
                                  fromtable=loadsource, toname='loadsourceshortname',
                                  use_order_of_sourcetbl=use_order_of_sourcetbl)

    def loadsourceids_from(self, sectorids=None):
        return self._map_using_sourcetbl(sectorids, tbl='TblLoadSource',
                                         fromcol='sectorid', tocol='loadsourceid')

    def single_loadsourcegroupid_from_loadsourcegroup_name(self, loadsourcegroupname):
        TblLoadSourceGroup = self.source.TblLoadSourceGroup  # get relevant source data
        return TblLoadSourceGroup['loadsourcegroupid'][TblLoadSourceGroup['loadsourcegroup'] ==
                                                       loadsourcegroupname].tolist()

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

        # ** LoadSources that are of the Ag or Septic sector only go on NONFED agency parcels **
        # So, first, identify the LoadSources that are in the Ag or Septic sector
        sectoridsToRemove = self.sector.ids_from_names(['Agriculture', 'Septic'])
        loadsourceids = list(self.loadsourceids_from(sectorids=sectoridsToRemove)['loadsourceid'])
        # Then, get the NONFED agencyid
        agencyidsToRemove = list(self.agency.ids_from_names(['NONFED'])['agencyid'])
        # Then, extract only the rows that aren't those loadsources and not NONFED
        tblreturn = tblsubset[~((tblsubset['loadsourceid'].isin(loadsourceids)) &
                                (~tblsubset['agencyid'].isin(agencyidsToRemove)))]

        return tblreturn

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
        lrsegids = self.lrseg.ids_from_names(names=lrsegs)
        agencyids = self.agency.ids_from_names(agencycodes=agencies)
        sectorids = self.sector.ids_from_names(names=sectors)

        # Generate all combinations of the lrseg, agency, sectors
        combos = list(product(lrsegids, agencyids))
        combos = pd.DataFrame(combos, columns=['lrsegid', 'agencyid'])

        # use [lrseg, agency] to get loadsourceids
        columnmask = ['lrsegid', 'agencyid', 'loadsourceid', 'unitid']
        tblloadsourceids1 = TblLandRiverSegmentAgencyLoadSource.loc[:, columnmask].merge(combos, how='inner')

        # use sectors/loadsourcegroups to get loadsourceids
        sectorid_df = pd.DataFrame(sectorids, columns=['sectorid'])
        tblloadsourceids2 = self.loadsourceids_from(sectorids=sectorid_df)

        # get the intersection of these two loadsourceid tables
        tblloadsourceids = tblloadsourceids1.merge(tblloadsourceids2, how='inner')

        # get the loadsource names from their ids
        columnmask = ['loadsourceid', 'loadsource']
        tblsubset = TblLoadSource.loc[:, columnmask].merge(tblloadsourceids, how='inner')

        return tblsubset.loc[:, ['loadsource']]

    def convert_land_slabidtable_loadsources_to_loadsourcegroups(self, slabidtable=None):
        TblLoadSourceGroupLoadSource = self.source.TblLoadSourceGroupLoadSource

        # Convert loadsourceids to loadsourcegroupids
        columnmask = ['loadsourcegroupid', 'loadsourceid']
        tblsubset = TblLoadSourceGroupLoadSource.loc[:, columnmask].merge(slabidtable, how='inner')
        tblsubset.drop(['loadsourceid'], axis=1, inplace=True)

        return tblsubset

    def convert_table_animals_to_animalgroups(self, table=None):
        TblAnimalGroupAnimal = self.source.TblAnimalGroupAnimal

        # Get the animalgroups that each animalid belongs to
        columnmask = ['animalgroupid', 'animalid']
        tblsubset = TblAnimalGroupAnimal.loc[:, columnmask].merge(table, how='inner')
        tblsubset.drop(['animalid'], axis=1, inplace=True)

        return tblsubset

    def appendLoadSourceSector_to_table_with_loadsourceid(self):
        pass

    def appendLoadSourceMajor_to_table_with_loadsourceid(self):
        pass