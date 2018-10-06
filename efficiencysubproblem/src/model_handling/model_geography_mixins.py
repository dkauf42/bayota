import pyomo.environ as oe


class ModelCountyGeoentitiesMixin(object):

    @staticmethod
    def _load_model_geographies(model, datahandler):
        print('ModelCountyGeoentitiesMixin._load_model_geographies()')

        model.COUNTIES = oe.Set(initialize=datahandler.COUNTIES)
        model.LRSEGS = oe.Set(initialize=datahandler.LRSEGS)
        model.CNTYLRSEGLINKS = oe.Set(initialize=datahandler.CNTYLRSEGLINKS, dimen=2)


class ModelLrsegGeoentitiesMixin(object):

    @staticmethod
    def _load_model_geographies(model, datahandler):
        print('ModelLrsegGeoentitiesMixin._load_model_geographies()')

        model.LRSEGS = oe.Set(initialize=datahandler.LRSEGS)