

class DataCountyGeoentitiesMixin(object):

    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
        print('DataCountyGeoentitiesMixin._load_set_geographies()')

        geodf = self.jeeves.county.add_lrsegs_to_counties(countystatestrs=geolist)

        if geodf.empty:
            raise ValueError('** no matching geographies found. please check scale and entities **')

        geodf = self.jeeves.lrseg.remove_outofcbws_lrsegs(lrsegdf=geodf)
        lrsegs_list = geodf.landriversegment.tolist()

        counties_list = geodf.countyid.tolist()
        cntylrseglinkslist = list(zip(lrsegs_list, counties_list))

        self.countysetlist = list(set(geodf.countystatestrs))
        self.countysetidlist = list(set(counties_list))
        self.COUNTIES = self.countysetidlist
        self.CNTYLRSEGLINKS = cntylrseglinkslist

        self._load_set_lrsegs_from_lrseg_list(TblLandRiverSegment, lrsegs_list)


class DataLrsegGeoentitiesMixin(object):

    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
        print('DataLrsegGeoentitiesMixin._load_set_geographies()')
        lrsegs_list = self.jeeves.lrseg.remove_outofcbws_lrsegs(lrseglist=geolist)

        if not lrsegs_list:
            raise ValueError('** no matching geographies found. please check scale and entities **')

        return self._load_set_lrsegs_from_lrseg_list(TblLandRiverSegment, lrsegs_list)
