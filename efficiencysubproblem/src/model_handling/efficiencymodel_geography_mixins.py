import pyomo.environ as oe


class ModelCountyMixin(object):

    @staticmethod
    def _load_model_geographies(model, datahandler):
        print('ModelCountyMixin._load_model_geographies()')

        model.COUNTIES = oe.Set(initialize=datahandler.COUNTIES)
        model.LRSEGS = oe.Set(initialize=datahandler.LRSEGS)
        model.CNTYLRSEGLINKS = oe.Set(initialize=datahandler.CNTYLRSEGLINKS, dimen=2)


class ModelLrsegMixin(object):

    @staticmethod
    def _load_model_geographies(model, datahandler):
        print('ModelLrsegMixin._load_model_geographies()')

        model.LRSEGS = oe.Set(initialize=datahandler.LRSEGS)