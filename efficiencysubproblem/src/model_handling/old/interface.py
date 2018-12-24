from .modelhandler_base import ModelHandlerBase
from .model_geography_mixins import ModelCountyGeoentitiesMixin, ModelLrsegGeoentitiesMixin
from .model_objective_mixins import ModelTotalCostMinObjMixin, ModelTotalLoadReductionMaxObjMixin
from .model_constraint_mixins import ModelPercentLoadReductionConstraintAtCountyLevelSumMixin,\
    ModelPercentLoadReductionConstraintAtLrsegLevelMixin,\
    ModelTotalCostUpperBoundConstraintMixin

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


class ModelHandlerLrsegWithCostObjective(ModelPercentLoadReductionConstraintAtLrsegLevelMixin,
                                         ModelTotalCostMinObjMixin,
                                         ModelLrsegGeoentitiesMixin,
                                         ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerCountyWithCostObjective(ModelPercentLoadReductionConstraintAtCountyLevelSumMixin,
                                          ModelTotalCostMinObjMixin,
                                          ModelCountyGeoentitiesMixin,
                                          ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerLrsegWithLoadObjective(ModelTotalCostUpperBoundConstraintMixin,
                                         ModelTotalLoadReductionMaxObjMixin,
                                         ModelLrsegGeoentitiesMixin,
                                         ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)


class ModelHandlerCountyWithLoadObjective(ModelTotalCostUpperBoundConstraintMixin,
                                          ModelTotalLoadReductionMaxObjMixin,
                                          ModelCountyGeoentitiesMixin,
                                          ModelHandlerBase):
    def __init__(self, datahandler=None):
        ModelHandlerBase.__init__(self, datahandler)