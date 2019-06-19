import pyomo.environ as oe

import logging
logger = logging.getLogger(__name__)


class ModelCountyGeoentitiesMixin(object):

    @staticmethod
    def _load_model_geographies(model, datahandler):
        logger.debug('Loading county geoentities')

        model.COUNTIES = oe.Set(initialize=datahandler.COUNTIES)
        model.LRSEGS = oe.Set(initialize=datahandler.LRSEGS)
        model.CNTYLRSEGLINKS = oe.Set(initialize=datahandler.CNTYLRSEGLINKS, dimen=2)


class ModelLrsegGeoentitiesMixin(object):

    @staticmethod
    def _load_model_geographies(model, datahandler):
        logger.debug('Loading lrseg geoentities')

        model.LRSEGS = oe.Set(initialize=datahandler.LRSEGS)