

class DataLrsegMixin(object):
    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
        print('DataLrsegMixin._load_set_geographies()')
        return self._load_set_lrsegs_from_lrseg_list(TblLandRiverSegment, geolist)
