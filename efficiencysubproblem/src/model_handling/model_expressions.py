import pyomo.environ as pe


def original_load_expr(mdl):
    """ Original Load Expression (with lrsegs aggregated together) """
    def original_load_rule(model, p):
        return sum([(model.phi[l, lmbda, p] * model.T[l, lmbda])
                    for l in model.LRSEGS
                    for lmbda in model.LOADSRCS])

    mdl.original_load_expr = pe.Expression(mdl.PLTNTS, rule=original_load_rule)
    return mdl


def original_load_for_each_lrseg_expr(mdl):
    """ Original Load Expression (quantified for each lrseg) """
    def original_load_rule_for_each_lrseg(model, l, p):
        return sum((model.phi[l, lmbda, p] * model.T[l, lmbda])
                   for lmbda in model.LOADSRCS)

    mdl.original_load_for_each_lrseg_expr = pe.Expression(mdl.LRSEGS,
                                                          mdl.PLTNTS,
                                                          rule=original_load_rule_for_each_lrseg)
    return mdl


def total_cost_expr(mdl):
    """ Total Cost Expression """
    def total_cost_rule(model):
        return sum([(model.c[b] * model.x[b, l, lmbda])
                    if ((b, lmbda) in model.BMPSRCLINKS)
                    else 0
                    for l in model.LRSEGS
                    for lmbda in model.LOADSRCS
                    for b in model.BMPS])

    mdl.total_cost_expr = pe.Expression(rule=total_cost_rule)
    return mdl


def percent_reduction_expr(mdl):
    """ Percent Relative Load Reduction (with lrsegs aggregated together) """

    # The model parameter 'originalload[p]' is required for this expression.
    mdl = original_load_expr(mdl)
    # loading before any new BMPs have been implemented
    mdl.originalload = pe.Param(mdl.PLTNTS,
                                initialize=lambda m, p: m.original_load_expr[p])

    def percent_reduction_rule(model, p):
        newload = sum([model.phi[l, lmbda, p] * model.T[l, lmbda] *
                       pe.prod([(1 - sum([(model.x[b, l, lmbda] / model.T[l, lmbda]) * model.E[b, p, l, lmbda]
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

        return ((model.originalload[p] - newload) / model.originalload[p]) * 100

    mdl.percent_reduction_expr = pe.Expression(mdl.PLTNTS, rule=percent_reduction_rule)
    return mdl


def percent_reduction_for_each_lrseg_expr(mdl):
    """ Percent Relative Load Reduction (quantified for each lrseg) """

    # The model parameter 'originalload[l, p]' is required for this expression.
    mdl = original_load_for_each_lrseg_expr(mdl)
    # loading before any new BMPs have been implemented
    mdl.originalload = pe.Param(mdl.LRSEGS,
                                mdl.PLTNTS,
                                initialize=lambda m, l, p: m.original_load_for_each_lrseg_expr[l, p])

    # Relative load reductions must be greater than the specified target percentages (tau)
    def percent_reduction_rule_for_each_lrseg(model, l, p):
        newload = sum([model.phi[l, lmbda, p] * model.T[l, lmbda] *
                       pe.prod([(1 - sum([(model.x[b, l, lmbda] / model.T[l, lmbda]) * model.E[b, p, l, lmbda]
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

        return temp

    mdl.percent_reduction_for_each_lrseg_expr = pe.Expression(mdl.PLTNTS,
                                                              mdl.LRSEGS,
                                                              rule=percent_reduction_rule_for_each_lrseg)
    return mdl


# def availableacres_expr(mdl):
#     """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """
#     def additive_bmps_acre_bound_rule(mdl, gamma, l, lmbda):
#         temp = sum([mdl.x[b, l, lmbda]
#                     if (((b, gamma) in mdl.BMPGRPING) & ((b, lmbda) in mdl.BMPSRCLINKS))
#                     else 0
#                     for b in mdl.BMPS])
#         return temp
#
#     mdl.availableacres_expr = pe.Expression(mdl.BMPGRPS,
#                                             mdl.LRSEGS,
#                                             mdl.LOADSRCS,
#                                             rule=additive_bmps_acre_bound_rule)
#     return mdl