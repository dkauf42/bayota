

class LrsegMixin(object):
    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
        print('LrsegMixin._load_set_geographies()')
        return self._load_set_lrsegs_from_lrseg_list(TblLandRiverSegment, geolist)
