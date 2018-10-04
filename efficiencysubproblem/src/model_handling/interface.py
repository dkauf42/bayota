from .modelhandler_base import ModelHandlerBase
from .efficiencymodel_geography_mixins import ModelCountyMixin, ModelLrsegMixin
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


class ModelHandlerLrsegWithCostObjective(ModelCostObjMixin, ModelLrsegMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerCountyWithCostObjective(ModelCostObjMixin, ModelCountyMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerLrsegWithLoadObjective(ModelLoadObjMixin, ModelLrsegMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerCountyWithLoadObjective(ModelLoadObjMixin, ModelCountyMixin, ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)