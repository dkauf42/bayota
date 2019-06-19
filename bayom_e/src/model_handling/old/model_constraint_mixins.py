import pyomo.environ as pe

import logging
logger = logging.getLogger(__name__)


class ModelPercentLoadReductionConstraintAtCountyLevelSumMixin(object):
    """
    Parameters:
        Original load indexed by [PLTNTS]
        tau indexed by [PLTNTS]

    Constraints:
        TargetPercentReduction indexed by [PLTNTS]

    """
    @staticmethod
    def _specify_model_original_load(model):
        # loading before any new BMPs have been implemented
        model.originalload = pe.Param(model.PLTNTS,
                                      initialize=lambda m, p: m.original_load_expr[p])

    @staticmethod
    def _load_model_constraints_other(model, datahandler):
        logger.debug('loading county level constraints')

        # target percent load reduction
        model.tau = pe.Param(model.PLTNTS,
                             initialize=datahandler.tau,
                             within=pe.NonNegativeReals,
                             mutable=True)

        # Relative load reductions
        model.TargetPercentReduction = pe.Constraint(model.PLTNTS,
                                                     rule=lambda m, p:   # lower, body, upper
                                                     (model.tau[p], model.percent_reduction_expr[p], None) )

        """ Deactivate unused P and S constraints"""
        # Retain only the Nitrogen load constraints, and deactivate the others
        model.TargetPercentReduction['P'].deactivate()
        model.TargetPercentReduction['S'].deactivate()


class ModelPercentLoadReductionConstraintAtLrsegLevelMixin(object):
    """
    Parameters:
        Original load indexed by [LRSEGS, PLTNTS]
        tau indexed by [LRSEGS, PLTNTS]

    Constraints:
        TargetPercentReduction indexed by [LRSEGS, PLTNTS]

    """
    @staticmethod
    def _specify_model_original_load(model):
        # loading before any new BMPs have been implemented
        model.originalload = pe.Param(model.LRSEGS,
                                      model.PLTNTS,
                                      initialize=lambda m, l, p: m.original_load_for_each_lrseg_expr[l, p])

    @staticmethod
    def _load_model_constraints_other(model, datahandler):
        logger.debug('loading lrseg level constraints')
        # print('ModelPercentLoadReductionConstraintAtLrsegLevelMixin._load_model_constraints_other()')

        # target percent load reduction
        model.tau = pe.Param(model.LRSEGS,
                             model.PLTNTS,
                             initialize=datahandler.tau,
                             within=pe.NonNegativeReals,
                             mutable=True)

        # Relative load reductions must be greater than the specified target percentages (tau)
        model.TargetPercentReduction = pe.Constraint(model.LRSEGS,
                                                     model.PLTNTS,
                                                     rule=lambda m, l, p:
                                                     (m.tau[l, p], m.percent_reduction_for_each_lrseg_expr[l, p], None))

        """ Deactivate unused P and S constraints"""
        # Retain only the Nitrogen load constraints, and deactivate the others
        for l in model.LRSEGS:
            model.TargetPercentReduction[l, 'P'].deactivate()
            model.TargetPercentReduction[l, 'S'].deactivate()


class ModelTotalCostUpperBoundConstraintMixin(object):
    """
    Parameters:
        totalcostupperbound indexed by []

    Constraints:
        Total_Cost indexed by []

    """
    @staticmethod
    def _load_model_constraints_other(model, datahandler):
        logger.debug('loading total cost upper bound constraint')
        # print('ModelTotalCostUpperBoundConstraintMixin._load_model_constraints_other()')

        # upper bound on total cost
        model.totalcostupperbound = pe.Param(initialize=datahandler.totalcostupperbound,
                                             within=pe.NonNegativeReals,
                                             mutable=True)

        model.Total_Cost = pe.Constraint(rule=lambda m: (None, m.total_cost_expr, m.totalcostupperbound))
