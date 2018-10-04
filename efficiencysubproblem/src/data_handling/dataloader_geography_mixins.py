

class DataCountyMixin(object):

    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
        print('DataCountyMixin._load_set_geographies()')
        """ """
        """ Counties and Land River Segments """
        geodf = self.jeeves.county.add_lrsegs_to_counties(countystatestrs=geolist)
        lrsegs_list = geodf.landriversegment.tolist()
        counties_list = geodf.countyid.tolist()
        cntylrseglinkslist = list(zip(lrsegs_list, counties_list))

        self.countysetlist = list(set(geodf.countystatestrs))
        self.countysetidlist = list(set(counties_list))
        self.COUNTIES = self.countysetidlist
        self.CNTYLRSEGLINKS = cntylrseglinkslist

        self._load_set_lrsegs_from_lrseg_list(TblLandRiverSegment, lrsegs_list)


class DataLrsegMixin(object):

    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
        print('DataLrsegMixin._load_set_geographies()')
        return self._load_set_lrsegs_from_lrseg_list(TblLandRiverSegment, geolist)
