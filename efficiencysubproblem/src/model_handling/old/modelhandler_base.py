import pyomo.environ as oe
# from .model_expressions import generate_expressions


class ModelHandlerBase:
    def __init__(self, datahandler):
        self.datahandler = datahandler
        self.model = self.build_subproblem_model(datahandler)

    def _load_model_geographies(self, model, datahandler):
        """ Overridden in Mixins """
        pass

    def _load_model_constraints_other(self, model, datahandler):
        """ Overridden in Mixins """
        pass

    def _load_model_objective(self, model):
        """ Overridden in Mixins """
        pass

    def _specify_model_original_load(self, model):
        """ Overridden in Mixins """
        pass

        # # loading before any new BMPs have been implemented
        # if geoscale == 'county':
        #     model.originalload = oe.Param(model.PLTNTS,
        #                                   initialize=lambda m, p: m.original_load_expr[p])
        # elif geoscale == 'lrseg':
        #     model.originalload = oe.Param(model.LRSEGS,
        #                                   model.PLTNTS,
        #                                   initialize=lambda m, l, p: m.original_load_for_each_lrseg_expr[l, p])
        # else:
        #     raise ValueError('geoscale unrecognized')

    @staticmethod
    def _load_model_constraint_availableacres(model):
        """ BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC """
        def additive_bmps_acre_bound_rule(model, gamma, l, lmbda):
            temp = sum([model.x[b, l, lmbda]
                        if (((b, gamma) in model.BMPGRPING) & ((b, lmbda) in model.BMPSRCLINKS))
                        else 0
                        for b in model.BMPS])
            return None, temp, model.T[l, lmbda]

        model.AdditiveBMPSAcreBound = oe.Constraint(model.BMPGRPS,
                                                    model.LRSEGS,
                                                    model.LOADSRCS,
                                                    rule=additive_bmps_acre_bound_rule)

    def _define_sets(self, model, datahandler):
        """ Sets """

        # pltnts = datahandler.PLTNTS,
        # counties = datahandler.COUNTIES,
        # lrsegs = datahandler.LRSEGS,
        # cntylrseglinks = datahandler.CNTYLRSEGLINKS,
        # bmps = datahandler.BMPS,
        # bmpgrps = datahandler.BMPGRPS,
        # bmpgrping = datahandler.BMPGRPING,
        # loadsrcs = datahandler.LOADSRCS,
        # bmpsrclinks = datahandler.BMPSRCLINKS,
        # bmpgrpsrclinks = datahandler.BMPGRPSRCLINKS,

        model.PLTNTS = oe.Set(initialize=datahandler.PLTNTS,
                              ordered=True,
                              doc="""Pollutants (N, P, or S).""")

        self._load_model_geographies(model, datahandler)  #lrsegs, counties, cntylrseglinks)
        # model.LRSEGS = oe.Set(initialize=lrsegs)

        model.BMPS = oe.Set(initialize=datahandler.BMPS, ordered=True)
        model.BMPGRPS = oe.Set(initialize=datahandler.BMPGRPS)
        model.BMPGRPING = oe.Set(initialize=datahandler.BMPGRPING, dimen=2)

        model.LOADSRCS = oe.Set(initialize=datahandler.LOADSRCS)

        model.BMPSRCLINKS = oe.Set(initialize=datahandler.BMPSRCLINKS, dimen=2)
        model.BMPGRPSRCLINKS = oe.Set(initialize=datahandler.BMPGRPSRCLINKS, dimen=2)

    def _define_params(self, model, datahandler):
        """ Parameters """
        # c = datahandler.c,
        # e = datahandler.E,
        # tau = datahandler.tau,
        # phi = datahandler.phi,
        model.c = oe.Param(model.BMPS,
                           initialize=datahandler.c,
                           within=oe.NonNegativeReals,
                           doc="""cost per acre of BMP b.""")
        model.E = oe.Param(model.BMPS,
                           model.PLTNTS,
                           model.LRSEGS,
                           model.LOADSRCS,
                           initialize=datahandler.E,
                           within=oe.NonNegativeReals,
                           doc='effectiveness per acre of BMP b')
        model.phi = oe.Param(model.LRSEGS,
                             model.LOADSRCS,
                             model.PLTNTS,
                             initialize=datahandler.phi,
                             within=oe.NonNegativeReals,
                             doc='base nutrient load per load source')
        model.T = oe.Param(model.LRSEGS,
                           model.LOADSRCS,
                           initialize=datahandler.T,
                           within=oe.NonNegativeReals,
                           doc='total acres available in an lrseg/load source')

    def build_subproblem_model(self, datahandler):
        # t = datahandler.T,
        # totalcostupperbound = datahandler.totalcostupperbound

        model = oe.ConcreteModel()

        self._define_sets(model, datahandler)

        """ Variables """
        model.x = oe.Var(model.BMPS,
                         model.LRSEGS,
                         model.LOADSRCS,
                         within=model.BMPSRCLINKS,
                         domain=oe.NonNegativeReals,
                         doc='Amount of each BMP to implement.')

        self._define_params(model, datahandler)

        """ Expressions """
        model = generate_expressions(model)

        self._specify_model_original_load(model)

        # # loading before any new BMPs have been implemented
        # def originalload_rule(model, l, p):
        #     temp = sum([(model.phi[l, lmbda, p] * model.T[l, lmbda])
        #                 for l in model.LRSEGS
        #                 for lmbda in model.LOADSRCS])
        #     return temp
        #
        # #         def originalload_rule(model, l, p):
        # #             return sum((model.phi[l, lmbda, p] * model.T[l, lmbda]) for lmbda in model.LOADSRCS)
        # #         model.originalload = oe.Param(model.LRSEGS,
        # #                                       model.PLTNTS,
        # #                                       initialize=originalload_rule)
        # model.originalload = oe.Param(model.PLTNTS,
        #                               initialize=originalload_rule)
        # # upper bound on total cost
        # model.totalcostupperbound = oe.Param(initialize=totalcostupperbound,
        #                                      within=oe.NonNegativeReals,
        #                                      mutable=True)

        """ Constraints """
        self._load_model_constraint_availableacres(model)
        self._load_model_constraints_other(model, datahandler)

        """ Objective Function """
        self._load_model_objective(model)

        return model