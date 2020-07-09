""" Components that are defined here can be added to a Pyomo model
"""

import pyomo.environ as pyo


def Available_Acres_Constraint(model) -> pyo.ConcreteModel:
    """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """

    def additive_bmps_acre_bound_rule(mdl, G, s, u, h):
        temp = sum([mdl.x[b, s, u, h]
                    if (((b, G) in mdl.BMPGRPING) & ((b, u) in mdl.BMPSRCLINKS))
                    else 0
                    for b in mdl.BMPS])
        return None, temp, mdl.alpha[s, u, h]

    model.Available_Acres_Constraint = pyo.Constraint(model.BMPGRPS,
                                                      model.PARCELS,
                                                      rule=additive_bmps_acre_bound_rule)
    return model
