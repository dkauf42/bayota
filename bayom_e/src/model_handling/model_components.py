import pyomo.environ as pyo


def Available_Acres_Constraint(model) -> pyo.ConcreteModel:
    """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """

    def additive_bmps_acre_bound_rule(model, gamma, l, lmbda):
        temp = sum([model.x[b, l, lmbda]
                    if (((b, gamma) in model.BMPGRPING) & ((b, lmbda) in model.BMPSRCLINKS))
                    else 0
                    for b in model.BMPS])
        return None, temp, model.alpha[l, lmbda]

    model.Available_Acres_Constraint = pyo.Constraint(model.BMPGRPS,
                                                      model.LRSEGS,
                                                      model.LOADSRCS,
                                                      rule=additive_bmps_acre_bound_rule)
    return model
