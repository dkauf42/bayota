import pandas as pd
import warnings

from sandbox.util.Jeeves.sourcehooks import SourceHook


class Lrseg(SourceHook):
    def __init__(self):
        """ Geography Methods """
        SourceHook.__init__(self)

    def all_names(self):
        pass

    def all_ids(self):
        pass

    def ids_from_names(self):
        pass

    def names_from_ids(self, lrsegids=None):
        lrsegids = self.forceToSingleColumnDataFrame(lrsegids, colname='landriversegment')
        return self.singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'landriversegment'],
                                  fromtable=lrsegids, toname='landriversegment')
        pass

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

    def lrsegids_from(self, lrsegnames=None, countystatestrs=None, countyid=None):
        kwargs = (lrsegnames, countystatestrs, countyid)
        kwargsNoDataFrames = [True if isinstance(x, pd.DataFrame) else x for x in kwargs]
        if self.checkOnlyOne(kwargsNoDataFrames) is False:
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
        getfrom = self.forceToSingleColumnDataFrame(getfrom, colname='landriversegment')
        return self.__singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'landriversegment'],
                                    fromtable=getfrom, toname='lrsegid')

    def __lrsegids_from_countystatestrs(self, getfrom=None):
        countyids = self.countyid_from_countystatestrs(getfrom=getfrom)
        return self.__lrsegids_from_countyid(getfrom=countyids)

    def __lrsegids_from_countyid(self, getfrom=None):
        getfrom = self.forceToSingleColumnDataFrame(getfrom, colname='countyid')
        return self.__singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'countyid'],
                                    fromtable=getfrom, toname='lrsegid')

    def lrsegids_from_geoscale_with_names(self, scale='', areanames=None):
        if scale == 'County':
            tblsubset = self.lrsegids_from(countystatestrs=areanames)
            return tblsubset.loc[:, ['lrsegid']]
        else:
            warnings.warn('Specified scale "%s" is unrecognized' % scale, RuntimeWarning)
            return None

    def countyids_from_lrsegids(self, lrsegids=None):
        return self.__singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'countyid'],
                                    fromtable=lrsegids, toname='countyid')