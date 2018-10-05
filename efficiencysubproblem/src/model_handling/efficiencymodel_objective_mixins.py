import pyomo.environ as oe


class ModelCostObjMixin(object):

    @staticmethod
    def _specify_model_original_load(model):
        # loading before any new BMPs have been implemented
        def originalload_rule(model, l, p):
            return sum((model.phi[l, lmbda, p] * model.T[l, lmbda]) for lmbda in model.LOADSRCS)
        model.originalload = oe.Param(model.LRSEGS,
                                      model.PLTNTS,
                                      initialize=originalload_rule)

    @staticmethod
    def _load_model_constraints_other(model, datahandler):
        print('ModelCostObjMixin._load_model_constraints_other()')

        # target percent load reduction
        model.tau = oe.Param(model.LRSEGS,
                             model.PLTNTS,
                             initialize=datahandler.tau,
                             within=oe.NonNegativeReals,
                             mutable=True)

        # Relative load reductions must be greater than the specified target percentages (tau)
        def target_percent_reduction_rule(model, l, p):
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
                           for lmbda in model.LOADSRCS])

            # Some lrsegs have 0 total load for some nutrients
            # E.g. N24031PM0_4640_4820 = Cabin John Creek, in Montgomery County
            # has 0 originalload for phosphorus.  This causes a ZeroDivisionError when Pyomo
            # tries to generate an expression for this rule.
            # To avoid this, we set the percent reduction here to zero no matter what, since
            # we can assume newload never increases from zero to a positive value.
            if model.originalload[l, p] != 0:
                temp = ((model.originalload[l, p] - newload) / model.originalload[l, p]) * 100
            else:
                temp = 0

            return model.tau[l, p], temp, None

        model.TargetPercentReduction = oe.Constraint(model.LRSEGS,
                                                     model.PLTNTS,
                                                     rule=target_percent_reduction_rule)

        """ Deactivate unused P and S constraints"""
        # Retain only the Nitrogen load constraints, and deactivate the others
        for l in model.LRSEGS:
            model.TargetPercentReduction[l, 'P'].deactivate()
            model.TargetPercentReduction[l, 'S'].deactivate()

    @staticmethod
    def _load_model_objective(model):
        print('ModelCostObjMixin._load_model_objective()')

        def obj_rule(model):
            return sum([(model.c[b] * model.x[b, l, lmbda])
                        if ((b, lmbda) in model.BMPSRCLINKS)
                        else 0
                        for l in model.LRSEGS
                        for lmbda in model.LOADSRCS
                        for b in model.BMPS])

        model.Total_Cost = oe.Objective(rule=obj_rule, sense=oe.minimize)

        return model


class ModelLoadObjMixin(object):

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
    def _load_model_constraints_other(model, datahandler):
        print('ModelLoadObjMixin._load_model_constraints_other()')

        # upper bound on total cost
        model.totalcostupperbound = oe.Param(initialize=datahandler.totalcostupperbound,
                                             within=oe.NonNegativeReals,
                                             mutable=True)

        def cost_rule(model):
            temp = sum([(model.c[b] * model.x[b, l, lmbda])
                        if ((b, lmbda) in model.BMPSRCLINKS)
                        else 0
                        for l in model.LRSEGS
                        for lmbda in model.LOADSRCS
                        for b in model.BMPS])
            return (None, temp, model.totalcostupperbound)

        model.Total_Cost = oe.Constraint(rule=cost_rule)

    @staticmethod
    def _load_model_objective(model):
        print('ModelLoadObjMixin._load_model_objective()')

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