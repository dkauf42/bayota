import pyomo.environ as pe


def Available_Acres_Constraint(model):
    """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """

    def additive_bmps_acre_bound_rule(model, gamma, l, lmbda):
        temp = sum([model.x[b, l, lmbda]
                    if (((b, gamma) in model.BMPGRPING) & ((b, lmbda) in model.BMPSRCLINKS))
                    else 0
                    for b in model.BMPS])
        return None, temp, model.T[l, lmbda]

    model.Available_Acres_Constraint = pe.Constraint(model.BMPGRPS,
                                                     model.LRSEGS,
                                                     model.LOADSRCS,
                                                     rule=additive_bmps_acre_bound_rule)
    return model
