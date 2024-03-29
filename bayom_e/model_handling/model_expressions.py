""" Expressions that are defined here will be added as components to a Pyomo model
"""

import pyomo.environ as pyo


def total_cost_expr(model) -> pyo.ConcreteModel:
    """ Total Cost Expression """
    def total_cost_rule(mdl):
        return pyo.quicksum((mdl.tau[b] * mdl.x[b, s, u, h])
                            for b in mdl.BMPS
                            for s, u, h in mdl.PARCELS)

    model.total_cost_expr = pyo.Expression(rule=total_cost_rule)
    return model


def original_load_for_one_parcel_expr(model) -> pyo.ConcreteModel:
    """ An expression to grab one parcel's base load """
    def original_load_rule_for_one_parcel(mdl, s, u, h, p):
        return mdl.phi[s, u, h, p] * mdl.alpha[s, u, h]

    model.original_load_for_one_parcel_expr = pyo.Expression(model.PARCELS,
                                                             model.PLTNTS,
                                                             rule=original_load_rule_for_one_parcel)
    return model


def original_load_expr(model) -> pyo.ConcreteModel:
    """ Original Load Expression (with lrsegs aggregated together) """
    def original_load_rule(mdl, p):
        return pyo.quicksum((mdl.phi[s, u, h, p] * mdl.alpha[s, u, h])
                            for s, u, h in mdl.PARCELS)

    model.original_load_expr = pyo.Expression(model.PLTNTS,
                                              rule=original_load_rule)
    return model


def original_load_for_each_loadsource_expr(model) -> pyo.ConcreteModel:
    """ Original Load Expression (with lrsegs aggregated together) """
    def original_load_rule_for_each_loadsource(mdl, thisu, p):
        origload = pyo.quicksum((mdl.phi[s, u, h, p] * mdl.alpha[s, u, h])
                       if (u == thisu)
                       else 0
                       for s, u, h in mdl.PARCELS)
        return origload

    model.original_load_for_each_loadsource_expr = pyo.Expression(model.LOADSRCS,
                                                                  model.PLTNTS,
                                                                  rule=original_load_rule_for_each_loadsource)
    return model


def original_load_for_each_lrseg_expr(model) -> pyo.ConcreteModel:
    """ Original Load Expression (quantified for each lrseg) """
    def original_load_rule_for_each_lrseg(mdl, thisl, p):
        return pyo.quicksum((mdl.phi[s, u, h, p] * mdl.alpha[s, u, h])
                   if (s == thisl)
                   else 0
                   for s, u, h in mdl.PARCELS)

    model.original_load_for_each_lrseg_expr = pyo.Expression(model.LRSEGS,
                                                             model.PLTNTS,
                                                             rule=original_load_rule_for_each_lrseg)
    return model


def new_load_expr(model) -> pyo.ConcreteModel:
    """ New Load (with lrsegs aggregated together) """
    def new_load_rule(mdl, p):
        newload = pyo.quicksum(mdl.phi[s, u, h, p] * mdl.alpha[s, u, h] *
                      pyo.prod([(1 - sum((mdl.x[b, s, u, h] / mdl.alpha[s, u, h]) * mdl.eta[b, s, u, p]
                                         if ((pyo.value(mdl.alpha[s, u, h]) > 1e-6) &
                                             ((b, G) in mdl.BMPGRPING) &
                                             ((b, u) in mdl.BMPSRCLINKS))
                                         else 0
                                         for b in mdl.BMPS))
                               if (G, u) in mdl.BMPGRPSRCLINKS
                               else 1
                               for G in mdl.BMPGRPS])
                      for s, u, h in mdl.PARCELS)

        return newload

    model.new_load_expr = pyo.Expression(model.PLTNTS,
                                         rule=new_load_rule)
    return model


def new_load_for_each_loadsource_expr(model) -> pyo.ConcreteModel:
    """ New Load (with lrsegs aggregated together) """
    def new_load_rule(mdl, thisu, p):
        newload = pyo.quicksum(mdl.phi[s, u, h, p] * mdl.alpha[s, u, h] *
                      pyo.prod([(1 - sum((mdl.x[b, s, u, h] / mdl.alpha[s, u, h]) * mdl.eta[b, s, u, p]
                                         if ((pyo.value(mdl.alpha[s, u, h]) > 1e-6) &
                                             ((b, G) in mdl.BMPGRPING) &
                                             ((b, u) in mdl.BMPSRCLINKS))
                                         else 0
                                         for b in mdl.BMPS))
                               if (G, u) in mdl.BMPGRPSRCLINKS
                               else 1
                               for G in mdl.BMPGRPS])
                      if (u == thisu)
                      else 0
                      for s, u, h in mdl.PARCELS)

        return newload

    model.new_load_for_each_loadsource_expr = pyo.Expression(model.LOADSRCS,
                                                             model.PLTNTS,
                                                             rule=new_load_rule)
    return model


def new_load_for_each_lrseg_expr(model) -> pyo.ConcreteModel:
    """ New Loa (quantified for each lrseg) """
    def new_load_rule_for_each_lrseg(mdl, thisl, p):
        newload = pyo.quicksum(mdl.phi[s, u, h, p] * mdl.alpha[s, u, h] *
                      pyo.prod([(1 - sum((mdl.x[b, s, u, h] / mdl.alpha[s, u, h]) * mdl.eta[b, s, u, p]
                                         if ((pyo.value(mdl.alpha[s, u, h]) > 1e-6) &
                                             ((b, gamma) in mdl.BMPGRPING) &
                                             ((b, u) in mdl.BMPSRCLINKS))
                                         else 0
                                         for b in mdl.BMPS))
                               if (gamma, u) in mdl.BMPGRPSRCLINKS
                               else 1
                               for gamma in mdl.BMPGRPS])
                      if (s == thisl)
                      else 0
                      for s, u, h in mdl.PARCELS)

        return newload

    model.new_load_for_each_lrseg_expr = pyo.Expression(model.LRSEGS,
                                                        model.PLTNTS,
                                                        rule=new_load_rule_for_each_lrseg)
    return model


def percent_reduction_expr(model) -> pyo.ConcreteModel:
    """ Percent Relative Load Reduction (with lrsegs aggregated together) """

    # The model parameters 'originalload[p]' and 'newload[p]' is required for this expression.
    # model = original_load_expr(model)
    # model = new_load_expr(model)

    # loading before any new BMPs have been implemented
    # model.originalload = pyo.Param(model.PLTNTS,
    #                                initialize=lambda m, p: pyo.value(m.original_load_expr[p]))

    def percent_reduction_rule(mdl, p):
        return ((mdl.original_load_expr[p] - mdl.new_load_expr[p]) / mdl.original_load_expr[p]) * 100

    model.percent_reduction_expr = pyo.Expression(model.PLTNTS,
                                                  rule=percent_reduction_rule)
    return model


def percent_reduction_for_each_lrseg_expr(model) -> pyo.ConcreteModel:
    """ Percent Relative Load Reduction (quantified for each lrseg) """

    # The model parameter 'originalload[s, p]' is required for this expression.
    model = original_load_for_each_lrseg_expr(model)
    model = new_load_for_each_lrseg_expr(model)
    # loading before any new BMPs have been implemented
    # model.originalload = pyo.Param(model.LRSEGS,
    #                                model.PLTNTS,
    #                                initialize=lambda m, s, p: m.original_load_for_each_lrseg_expr[s, p])

    # Relative load reductions must be greater than the specified target percentages (Theta)
    def percent_reduction_rule_for_each_lrseg(mdl, s, p):

        # Some lrsegs have 0 total load for some nutrients
        # E.g. N24031PM0_4640_4820 = Cabin John Creek, in Montgomery County
        # has 0 originalload for phosphorus.  This causes a ZeroDivisionError when Pyomo
        # tries to generate an expression for this rule.
        # To avoid this, we set the percent reduction here to zero no matter what, since
        # we can assume newload never increases from zero to a positive value.
        if mdl.originalload[s, p] != 0:
            temp = ((mdl.original_load_for_each_lrseg_expr[s, p] - mdl.new_load_for_each_lrseg_expr[s, p]) / mdl.original_load_for_each_lrseg_expr[s, p]) * 100
        else:
            temp = 0

        return temp

    model.percent_reduction_for_each_lrseg_expr = pyo.Expression(model.PLTNTS,
                                                                 model.LRSEGS,
                                                                 rule=percent_reduction_rule_for_each_lrseg)
    return model


# def availableacres_expr(mdl):
#     """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """
#     def additive_bmps_acre_bound_rule(mdl, gamma, l, u):
#         temp = sum([mdl.x[b, l, u]
#                     if (((b, gamma) in mdl.BMPGRPING) & ((b, u) in mdl.BMPSRCLINKS))
#                     else 0
#                     for b in mdl.BMPS])
#         return temp
#
#     mdl.availableacres_expr = pyo.Expression(mdl.BMPGRPS,
#                                             mdl.LRSEGS,
#                                             mdl.LOADSRCS,
#                                             rule=additive_bmps_acre_bound_rule)
#     return mdl
