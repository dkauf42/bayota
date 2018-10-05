from .modelhandler_base import ModelHandlerBase
from .efficiencymodel_geography_mixins import ModelCountyGeoentitiesMixin, ModelLrsegGeoentitiesMixin
from .efficiencymodel_objective_mixins import ModelCostObjMixin, ModelLoadObjMixin

from efficiencysubproblem.src.data_handling.interface import get_loaded_data_handler


def get_loaded_model_handler(objectivetype, geoscale, geoentities, savedata2file=False):
    """ This function calls up a DataHandler and then creates a ModelHandler """

    datahandler = get_loaded_data_handler(objectivetype=objectivetype, geoscale=geoscale,
                                          geoentities=geoentities, savedata2file=savedata2file)

    if objectivetype == 'costmin':
        if geoscale == 'lrseg':
            modelhandler = ModelHandlerLrsegWithCostObjective(datahandler=datahandler)
        elif geoscale == 'county':
            modelhandler = ModelHandlerCountyWithCostObjective(datahandler=datahandler)
        else:
            raise ValueError('unrecognized "geoscale"')

    elif objectivetype == 'loadreductionmax':
        if geoscale == 'lrseg':
            modelhandler = ModelHandlerLrsegWithLoadObjective(datahandler=datahandler)
        elif geoscale == 'county':
            modelhandler = ModelHandlerCountyWithLoadObjective(datahandler=datahandler)
        else:
            raise ValueError('unrecognized "geoscale"')

    else:
        raise ValueError('unrecognized objectivetype')

    return modelhandler


""" Different ModelHandler classes inherit from different Mixin combinations """


class ModelHandlerLrsegWithCostObjective(ModelCostObjMixin, ModelLrsegGeoentitiesMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerCountyWithCostObjective(ModelCostObjMixin, ModelCountyGeoentitiesMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerLrsegWithLoadObjective(ModelLoadObjMixin, ModelLrsegGeoentitiesMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerCountyWithLoadObjective(ModelLoadObjMixin, ModelCountyGeoentitiesMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)