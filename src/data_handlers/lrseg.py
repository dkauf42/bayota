from .dataloaders import DataLoader


class Lrseg(DataLoader):
    def __init__(self, save2file=True, geolist=None):
        # super constructor
        DataLoader.__init__(self, save2file=save2file, geolist=geolist)

    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
        return self._load_set_lrsegs_from_lrseg_list(TblLandRiverSegment, geolist)
