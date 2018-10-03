import pyomo.environ as oe

from .efficiencymodel import EfficiencyModel
from efficiencysubproblem.src.data_handlers.dataloader_types import CountyWithLoadReductionConstraint


class CostObj(EfficiencyModel):
    def __init__(self):
        # super constructor
        EfficiencyModel.__init__(self)

    def load_data(self, savedata2file=False, county_list=None):
        data = CountyWithLoadReductionConstraint(save2file=savedata2file, geolist=county_list)
        return data

    def create_concrete(self, data):
        # Note that there is no need to call create_instance on a ConcreteModel
        mdl = self.build_subproblem_model(pltnts=data.PLTNTS,
                                          counties=data.COUNTIES,
                                          lrsegs=data.LRSEGS,
                                          cntylrseglinks=data.CNTYLRSEGLINKS,
                                          bmps=data.BMPS,
                                          bmpgrps=data.BMPGRPS,
                                          bmpgrping=data.BMPGRPING,
                                          loadsrcs=data.LOADSRCS,
                                          bmpsrclinks=data.BMPSRCLINKS,
                                          bmpgrpsrclinks=data.BMPGRPSRCLINKS,
                                          c=data.c,
                                          e=data.E,
                                          tau=data.tau,
                                          phi=data.phi,
                                          t=data.T)

        # Retain only the Nitrogen load constraints, and deactivate the others
        for l in mdl.LRSEGS:
            mdl.TargetPercentReduction[l, 'P'].deactivate()
            mdl.TargetPercentReduction[l, 'S'].deactivate()

        return mdl

    @staticmethod
    def build_subproblem_model(pltnts, counties, lrsegs, cntylrseglinks,
                               bmps, bmpgrps, bmpgrping,
                               loadsrcs, bmpsrclinks, bmpgrpsrclinks,
                               c, e, tau, phi, t):

        model = oe.ConcreteModel()

        """ Sets """
        model.PLTNTS = oe.Set(initialize=pltnts)
        model.COUNTIES = oe.Set(initialize=counties)
        model.LRSEGS = oe.Set(initialize=lrsegs)
        model.CNTYLRSEGLINKS = oe.Set(initialize=cntylrseglinks, dimen=2)

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
        # target percent load reduction
        model.tau = oe.Param(model.LRSEGS,
                             model.PLTNTS,
                             initialize=tau,
                             within=oe.NonNegativeReals,
                             mutable=True)
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

        """ Variables """
        model.x = oe.Var(model.BMPS,
                         model.LRSEGS,
                         model.LOADSRCS,
                         within=model.BMPSRCLINKS,
                         domain=oe.NonNegativeReals)

        """ Constraints """
        # Relative load reductions must be greater than the specified target percentages (tau)
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
            return (model.tau[l, p], temp, None)
        model.TargetPercentReduction = oe.Constraint(model.LRSEGS,
                                                     model.PLTNTS,
                                                     rule=TargetPercentReduction_rule)

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
        def ObjRule(model):
            return sum([(model.c[b] * model.x[b, l, lmbda])
                        if ((b, lmbda) in model.BMPSRCLINKS)
                        else 0
                        for l in model.LRSEGS
                        for lmbda in model.LOADSRCS
                        for b in model.BMPS])
        model.Total_Cost = oe.Objective(rule=ObjRule, sense=oe.minimize)

        return model

