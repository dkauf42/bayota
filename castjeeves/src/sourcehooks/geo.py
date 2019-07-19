import pandas as pd
import warnings

from .sourcehooks import SourceHook
from .lrseg import Lrseg
from .county import County


class Geo(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Geography Methods """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        self.lrseg = Lrseg(sourcedata=sourcedata, metadata=metadata)
        self.county = County(sourcedata=sourcedata, metadata=metadata)

    def all_geotypes(self):
        TblGeoType = self.source.TblGeographyType  # get relevant source data
        TblGeoType = TblGeoType.loc[TblGeoType['castscenariogeographytype'] == True]
        return TblGeoType.loc[:, ['geographytypeid', 'geographytype', 'geographytypefullname']]


    def geotypeid_from_geotypename(self, geotype):
        return self._map_using_sourcetbl(geotype, tbl='TblGeographyType',
                                         tocol='geographytypeid', fromcol='geographytypefullname')

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

    def geonames_from_lrsegid(self, lrsegids=None):
        geographyids = self.singleconvert(sourcetbl='TblGeographyLrSeg', toandfromheaders=['lrsegid', 'geographyid'],
                                          fromtable=lrsegids, toname='geographyid', use_order_of_sourcetbl=False)

        allgeofullnames_of_type = self.geonames_from_geotypename(['Land River Segment indicating if in or out of CBWS'])

        geographyfullnames = self.singleconvert(sourcetbl='TblGeography', toandfromheaders=['geographyid', 'geographyfullname'],
                                                fromtable=geographyids, toname='geographyfullname', use_order_of_sourcetbl=False)

        # Get intersection of (1) all fullnames of lrseg type and (2) the input data fullnames
        return pd.Series(list(set(allgeofullnames_of_type) & set(geographyfullnames['geographyfullname'])))


    def lrsegids_from(self, lrsegnames=None, countystatestrs=None, countyid=None):
        kwargs = (lrsegnames, countystatestrs, countyid)
        kwargsNoDataFrames = [True if isinstance(x, pd.DataFrame) else x for x in kwargs]
        if self.checkOnlyOne(kwargsNoDataFrames) is False:
            raise ValueError('One and only one keyword argument must be specified')

        if lrsegnames is not None:
            return self.lrseg.ids_from_names(names=lrsegnames)
        elif countystatestrs is not None:
            return self.__lrsegids_from_countystatestrs(getfrom=countystatestrs)
        elif countyid is not None:
            return self.__lrsegids_from_countyid(getfrom=countyid)
        else:
            raise ValueError('unrecognized input')

    def __lrsegids_from_countystatestrs(self, getfrom=None):
        countyids = self.county.countyid_from_countystatestrs(getfrom=getfrom)
        return self.__lrsegids_from_countyid(getfrom=countyids)

    def __lrsegids_from_countyid(self, getfrom=None, todict=True, flatten_to_set=False):
        return self._map_using_sourcetbl(getfrom, tbl='TblLandRiverSegment',
                                         fromcol='countyid', tocol='lrsegid',
                                         todict=todict, flatten_to_set=flatten_to_set)

    def lrsegids_from_geoscale_with_names(self, scale='', areanames=None):
        if scale == 'County':
            tblsubset = self.lrsegids_from(countystatestrs=areanames)
            return tblsubset.loc[:, ['lrsegid']]
        elif scale == "Land River Segment indicating if in or out of CBWS":
            segstrlist = [x.split("-")[1].split("(")[0] for x in areanames]
            return self.singleconvert(sourcetbl='TblLandRiverSegment',
                                      toandfromheaders=['lrsegid', 'landriversegment'],
                                      fromtable=self.forceToSingleColumnDataFrame(segstrlist,
                                                                                  colname='landriversegment'),
                                      toname='lrsegid')
        else:
            raise ValueError('The specified scale ("%s") is unsupported' % scale)

    def countyids_from_lrsegids(self, lrsegids=None):
        return self._map_using_sourcetbl(lrsegids, tbl='TblLandRiverSegment',
                                         fromcol='lrsegid', tocol='countyid')

    def statenames_from_lrsegids(self, lrsegids=None):
        return self._map_using_multiple_sourcetbls(lrsegids,
                                                   tbls=['TblLandRiverSegment', 'TblState'],
                                                   column_sequence=['lrsegid', 'stateid', 'stateabbreviation'])
