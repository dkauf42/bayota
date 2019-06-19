
import logging
logger = logging.getLogger(__name__)


class DataCountyGeoentitiesMixin(object):

    def _load_set_geographies(self, jeeves, geolist=None):
        logger.debug('loading county geoentities')

        geodf = jeeves.county.add_lrsegs_to_counties(countystatestrs=[x.replace('Washington, DC',
                                                                                'District of Columbia, DC')
                                                                      for x in geolist])

        if geodf.empty:
            raise ValueError('** no matching geographies found. please check scale and entities **')

        geodf = jeeves.lrseg.remove_outofcbws_lrsegs(lrsegdf=geodf)
        lrsegs_list = geodf.landriversegment.tolist()

        counties_list = geodf.countyid.tolist()
        cntylrseglinkslist = list(zip(lrsegs_list, counties_list))

        self.countysetlist = list(set(geodf.countystatestrs))
        self.countysetidlist = list(set(counties_list))
        self.COUNTIES = self.countysetidlist
        self.CNTYLRSEGLINKS = cntylrseglinkslist

        self._load_set_lrsegs_from_lrseg_list(jeeves, lrsegs_list)


class DataLrsegGeoentitiesMixin(object):

    def _load_set_geographies(self, jeeves, geolist=None):
        logger.debug('loading lrseg geoentities')
        lrsegs_list = jeeves.lrseg.remove_outofcbws_lrsegs(lrseglist=geolist)

        if not lrsegs_list:
            raise ValueError('** no matching geographies found. please check scale and entities **')

        return self._load_set_lrsegs_from_lrseg_list(jeeves, lrsegs_list)
