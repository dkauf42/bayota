import pyomo.environ as oe


class ModelTotalCostMinObjMixin(object):
    """
    Objective:
        Total_Cost indexed by []

    """

    @staticmethod
    def _load_model_objective(model):
        print('ModelTotalCostMinObjMixin._load_model_objective()')

        def obj_rule(model):
            return sum([(model.c[b] * model.x[b, l, lmbda])
                        if ((b, lmbda) in model.BMPSRCLINKS)
                        else 0
                        for l in model.LRSEGS
                        for lmbda in model.LOADSRCS
                        for b in model.BMPS])

        model.Total_Cost = oe.Objective(rule=obj_rule, sense=oe.minimize)

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
        def originalload_rule(model, p):
            temp = sum([(model.phi[l, lmbda, p] * model.T[l, lmbda])
                        for l in model.LRSEGS
                        for lmbda in model.LOADSRCS])
            return temp
        model.originalload = oe.Param(model.PLTNTS,
                                      initialize=originalload_rule)

    @staticmethod
    def _load_model_objective(model):
        print('ModelTotalLoadReductionMaxObjMixin._load_model_objective()')

        # Relative load reductions
        def percent_reduction_rule(model, p):
            newload = sum([model.phi[l, lmbda, p] * model.T[l, lmbda] *
                           oe.prod([(1 - sum([(model.x[b, l, lmbda] / model.T[l, lmbda]) * model.E[b, p, l, lmbda]
                                              if ((model.T[l, lmbda] > 1e-6) &
                                                  ((b, gamma) in model.BMPGRPING) &
                                                  ((b, lmbda) in model.BMPSRCLINKS))
                                              else 0
                                              for b in model.BMPS]))
                                    if (gamma, lmbda) in model.BMPGRPSRCLINKS
                                    else 1
                                    for gamma in model.BMPGRPS])
                           for l in model.LRSEGS
                           for lmbda in model.LOADSRCS])
            temp = ((model.originalload[p] - newload) / model.originalload[p]) * 100
            return temp

        model.PercentReduction = oe.Objective(model.PLTNTS,
                                              rule=percent_reduction_rule,
                                              sense=oe.maximize)

        """ Deactivate unused P and S objectives """
        # Retain only the Nitrogen load objective, and deactivate the others
        model.PercentReduction['P'].deactivate()
        model.PercentReduction['S'].deactivate()