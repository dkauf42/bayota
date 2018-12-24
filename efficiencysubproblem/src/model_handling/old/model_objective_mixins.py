import pyomo.environ as pe

import logging
logger = logging.getLogger(__name__)


class ModelTotalCostMinObjMixin(object):
    """
    Objective:
        Total_Cost indexed by []
    """
    @staticmethod
    def _load_model_objective(model):
        logger.debug('Loading total cost min objective')
        model.Total_Cost = pe.Objective(rule=model.total_cost_expr, sense=pe.minimize)
        return model


class ModelTotalLoadReductionMaxObjMixin(object):
    """
    Parameters:
        Original load indexed by [PLTNTS]

    Objective:
        PercentReduction indexed by [PLTNTS]

    """
    @staticmethod
    def _specify_model_original_load(model):
        # loading before any new BMPs have been implemented
        model.originalload = pe.Param(model.PLTNTS,
                                      initialize=lambda m, p: m.original_load_expr[p])

    @staticmethod
    def _load_model_objective(model):
        logger.debug('Loading total load reduction max objective')

        # Relative load reductions
        model.PercentReduction = pe.Objective(model.PLTNTS,
                                              rule=lambda m, p: model.percent_reduction_expr[p],
                                              sense=pe.maximize)

        """ Deactivate unused P and S objectives """
        # Retain only the Nitrogen load objective, and deactivate the others
        model.PercentReduction['P'].deactivate()
        model.PercentReduction['S'].deactivate()