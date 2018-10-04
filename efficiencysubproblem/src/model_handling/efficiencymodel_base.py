import pyomo.environ as oe


class EfficiencyModelBase:
    def __init__(self, data):
        self.model = self.build_subproblem_model(data)

    def _load_model_geographies(self, model, lrsegs, counties, cntylrseglinks):
        """ Overridden in Mixins """
        pass

    def _load_model_constraint_availableacres(self, model):
        """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """
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

    def _load_model_constraints_other(self, model):
        """ Overridden in Mixins """
        pass

    def _load_model_objective(self, model):
        """ Overridden in Mixins """
        pass

    def build_subproblem_model(self, data):

        pltnts = data.PLTNTS,
        counties = data.COUNTIES,
        lrsegs = data.LRSEGS,
        cntylrseglinks = data.CNTYLRSEGLINKS,
        bmps = data.BMPS,
        bmpgrps = data.BMPGRPS,
        bmpgrping = data.BMPGRPING,
        loadsrcs = data.LOADSRCS,
        bmpsrclinks = data.BMPSRCLINKS,
        bmpgrpsrclinks = data.BMPGRPSRCLINKS,
        c = data.c,
        e = data.E,
        tau = data.tau,
        phi = data.phi,
        t = data.T,
        totalcostupperbound = data.totalcostupperbound

        model = oe.ConcreteModel()

        """ Sets """
        model.PLTNTS = oe.Set(initialize=pltnts,
                              ordered=True)

        self._load_model_geographies(model, lrsegs, counties, cntylrseglinks)
        # model.LRSEGS = oe.Set(initialize=lrsegs)

        model.BMPS = oe.Set(initialize=bmps, ordered=True)
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
        def originalload_rule(model, p):
            temp = sum([(model.phi[l, lmbda, p] * model.T[l, lmbda])
                        for l in model.LRSEGS
                        for lmbda in model.LOADSRCS])
            return temp

        model.originalload = oe.Param(model.PLTNTS,
                                      initialize=originalload_rule)
        # # upper bound on total cost
        # model.totalcostupperbound = oe.Param(initialize=totalcostupperbound,
        #                                      within=oe.NonNegativeReals,
        #                                      mutable=True)

        """ Variables """
        model.x = oe.Var(model.BMPS,
                         model.LRSEGS,
                         model.LOADSRCS,
                         within=model.BMPSRCLINKS,
                         domain=oe.NonNegativeReals)

        """ Constraints """
        self._load_model_constraint_availableacres(model)
        self._load_model_constraints_other(model)

        """ Objective Function """
        self._load_model_objective(model)

        return model
