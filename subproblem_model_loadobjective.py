import pyomo.environ as oe
from pyomo.opt import SolverFactory


def build_subproblem_model(pltnts, lrsegs, bmps, bmpgrps, bmpgrping, loadsrcs, bmpsrclinks, bmpgrpsrclinks,
                           c, e, phi, t, totalcostupperbound):

    model = oe.ConcreteModel()

    """ Sets """
    model.PLTNTS = oe.Set(initialize=pltnts)
    model.LRSEGS = oe.Set(initialize=lrsegs)

    model.BMPS = oe.Set(initialize=bmps)
    model.BMPGRPS = oe.Set(initialize=bmpgrps)
    model.BMPGRPING = oe.Set(initialize=bmpgrping, dimen=2)

    model.LOADSRCS = oe.Set(initialize=loadsrcs)

    model.BMPSRCLINKS = oe.Set(initialize=bmpsrclinks, dimen=2)
    model.BMPGRPSRCLINKS = oe.Set(initialize=bmpgrpsrclinks, dimen=2)

    """ Parameters """
    # cost per acre of BMP b
    model.c = oe.Param(model.BMPS,
                       initialize=c,
                       within=oe.NonNegativeReals)
    # effectiveness per acre of BMP b
    model.E = oe.Param(model.BMPS,
                       model.PLTNTS,
                       model.LRSEGS,
                       model.LOADSRCS,
                       initialize=e,
                       within=oe.NonNegativeReals)
    # base nutrient load per load source
    model.phi = oe.Param(model.LRSEGS,
                         model.LOADSRCS,
                         model.PLTNTS,
                         initialize=phi,
                         within=oe.NonNegativeReals)
    # total acres available in an lrseg/load source
    model.T = oe.Param(model.LRSEGS,
                       model.LOADSRCS,
                       initialize=t,
                       within=oe.NonNegativeReals)
    # loading before any new BMPs have been implemented
    def originalload_rule(model, l, p):
        return sum((model.phi[l, lmbda, p] * model.T[l, lmbda]) for lmbda in model.LOADSRCS)
    model.originalload = oe.Param(model.LRSEGS,
                                  model.PLTNTS,
                                  initialize=originalload_rule)
    # upper bound on total cost
    model.totalcostupperbound = oe.Param(initialize=totalcostupperbound,
                                         within=oe.NonNegativeReals)

    """ Variables """
    model.x = oe.Var(model.BMPS,
                     model.LRSEGS,
                     model.LOADSRCS,
                     within=model.BMPSRCLINKS,
                     domain=oe.NonNegativeReals)

    """ Constraints """
    def Cost_rule(model):
        temp = sum([(model.c[b] * model.x[b, l, lmbda])
                    if ((b, lmbda) in model.BMPSRCLINKS)
                    else 0
                    for l in model.LRSEGS
                    for lmbda in model.LOADSRCS
                    for b in model.BMPS])
        return (None, temp, model.totalcostupperbound)
    model.Total_Cost = oe.Constraint(rule=Cost_rule)

    # BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC
    def AdditiveBMPSAcreBound_rule(model, gamma, l, lmbda):
        temp = sum([model.x[b, l, lmbda]
                    if (((b, gamma) in model.BMPGRPING) & ((b, lmbda) in model.BMPSRCLINKS))
                    else 0
                    for b in model.BMPS])
        return (None, temp, model.T[l, lmbda])
    model.AdditiveBMPSAcreBound = oe.Constraint(model.BMPGRPS,
                                                model.LRSEGS,
                                                model.LOADSRCS,
                                                rule=AdditiveBMPSAcreBound_rule)

    """ Objective Function """
    # Relative load reductions
    def TargetPercentReduction_rule(model, l, p):
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
        temp = ((model.originalload[l, p] - newload) / model.originalload[l, p]) * 100
        return temp
    model.TargetPercentReduction = oe.Objective(model.LRSEGS,
                                                model.PLTNTS,
                                                rule=TargetPercentReduction_rule,
                                                sense=oe.minimize)

    return model

