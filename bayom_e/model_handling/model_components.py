import pyomo.environ as pyo


def Available_Acres_Constraint(model) -> pyo.ConcreteModel:
    """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """

    def additive_bmps_acre_bound_rule(mdl, gamma, l, u, h):
        temp = sum([mdl.x[b, l, u, h]
                    if (((b, gamma) in mdl.BMPGRPING) & ((b, u) in mdl.BMPSRCLINKS))
                    else 0
                    for b in mdl.BMPS])
        return None, temp, mdl.alpha[l, u, h]

    model.Available_Acres_Constraint = pyo.Constraint(model.BMPGRPS,
                                                      model.PARCELS,
                                                      rule=additive_bmps_acre_bound_rule)
    return model
