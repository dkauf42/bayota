from .dataloaders import DataLoader


class County(DataLoader):
    def __init__(self, save2file=True, geolist=None):
        # Additional attributes for County
        self.countysetlist = []
        self.countysetidlist = []
        self.COUNTIES = []
        self.CNTYLRSEGLINKS = []

        # super constructor
        DataLoader.__init__(self, save2file=save2file, geolist=geolist)

    def _load_set_geographies(self, TblLandRiverSegment, geolist=None):
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
