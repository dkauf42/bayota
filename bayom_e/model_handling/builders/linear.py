""" Build a LP variant of the Efficiency BMP model (A subclass of ModelBuilder)
"""

# Generic/Built-in
import logging
from typing import Dict
from itertools import product

# Computation
import pandas as pd
import pyomo.environ as pyo

# BAYOTA
from bayom_e.model_handling.builders.modelbuilder import ModelBuilder

default_logger = logging.getLogger(__name__)


class LinearVariant(ModelBuilder):
    """ Used to build a LP variant of the Efficiency BMP model (A subclass of ModelBuilder)
    """

    def __init__(self, logger=default_logger):
        """ Please see help(LinearVariant) for more info """
        ModelBuilder.__init__(self, logger=logger)

    def build_skeleton(self, dataplate, geoscale, target_load: Dict) -> pyo.ConcreteModel:
        """Nonlinear variant of the efficiency BMP model

        Skeleton
        - includes Sets, Parameters, and Variables.
        - does not include Objective, Constraints, or any other Expressions

        Notes:
        - no indexing by nutrient (assumed single nutrient)
        - no indexing by agency

        """
        model = pyo.ConcreteModel()

        # *************************
        # SETS
        # *************************
        model.PLTNTS = pyo.Set(initialize=dataplate.PLTNTS, ordered=True,
                               doc="""Pollutants (N, P, or S).""")

        # PARCELS
        model.LRSEGS = pyo.Set(initialize=dataplate.LRSEGS)
        model.LOADSRCS = pyo.Set(initialize=dataplate.LOADSRCS)
        model.AGENCIES = pyo.Set(initialize=dataplate.AGENCIES)
        model.PARCELS = pyo.Set(initialize=dataplate.PARCELS, within=model.LRSEGS*model.LOADSRCS*model.AGENCIES)

        # BMPS [Nelson's change Note: added b0]
        model.BMPS = pyo.Set(initialize=dataplate.BMPS + ['b0'], ordered=True)
        model.BMPGRPS = pyo.Set(initialize=dataplate.BMPGRPS)

        # # BMPs in each BMPGRP
        # self.create_2dim_set_component(model, dataplate.BMPGRPING, 'BMPGRPING')
        #
        # # BMPs in each LOADSRC
        # self.create_2dim_set_component(model, dataplate.BMPSRCLINKS, 'BMPSRCLINKS')
        #
        # # BMPGRPs in each LOADSRC
        # self.create_2dim_set_component(model, dataplate.BMPGRPSRCLINKS, 'BMPGRPSRCLINKS')

        # Create a dictionary that maps load source -> BMP group names
        allowable_groups_for_loadsource = dataplate.BMPGRPSRCLINKS.copy()

        # Create a dictionary that maps load source -> BMP group names
        allowable_bmps_for_loadsource = dataplate.BMPSRCLINKS.copy()

        # Add 'null_group' BMP group for load sources that are not
        # linked to any BMP groups
        for u in model.LOADSRCS:
            if u not in allowable_groups_for_loadsource:
                allowable_groups_for_loadsource[u] = ['null_group']

        """ Danny: adding the dictionary for parcels """
        # Create a dictionary that maps parcel -> BMP group names
        allowable_groups_for_parcel = {}
        for p in dataplate.PARCELS:
            allowable_groups_for_parcel[p] = allowable_groups_for_loadsource[p[1]]

        def bmp_cost_effectiveness_on_parcel(bmp, parcel):
            """ A BMP's cost-effectiveness (specific to each parcel) is calculated. """
            ce = 0
            if b != 'b0':  # b0 ('do-nothing bmp') will just have a cost-effectiveness of zero
                bmp_cost = dataplate.tau[bmp]
                if bmp_cost == 0:
                    ce = 999  # Divide-by-zero error is avoided.
                else:
                    ce = dataplate.eta[bmp, parcel[0], parcel[1], 'N'] / bmp_cost
            return ce

        """ The most cost-efficient BMP for every parcel (p) is retrieved. """
        most_effective_bmp_for_parcel = {}
        load_sources_without_bmps = []
        for i, p in enumerate(dataplate.PARCELS):
            # This parcel is skipped if no bmps can be applied to its load source.
            if not (p[1] in allowable_bmps_for_loadsource):
                if p[1] not in load_sources_without_bmps:
                    load_sources_without_bmps.append(p[1])
                    print(f"Not found: any bmps for load source <{p[1]}>.")
                continue

            # Cost-effectivenesses of all applicable bmps are retrieved, then sorted highest to lowest.
            cost_effectiveness_list = []
            for b in allowable_bmps_for_loadsource[p[1]]:
                cost_effectiveness = bmp_cost_effectiveness_on_parcel(b, p)
                cost_effectiveness_list.append((b, cost_effectiveness))
            most_cost_effective = sorted(cost_effectiveness_list, key=lambda x: x[1], reverse=True)[0]
            most_effective_bmp_for_parcel[p] = most_cost_effective[0]

        # df = pd.DataFrame_from_dict(dataplate.eta)

        # Feasible Assignments
        #   enumerate all combinations of bmps (with one from each group)
        # bmpgrping_listoflists = [v for _, v in dataplate.BMPGRPING.items()]
        # feasible_assignments = list(product(*bmpgrping_listoflists))
        # print(len(feasible_assignments))
        # fi_dict_ikeys = {i: f for (i, f) in enumerate(feasible_assignments)}
        # fi_dict_fkeys = {f: i for (i, f) in enumerate(feasible_assignments)}
        # fi = list(range(0, len(feasible_assignments)))
        # model.F = pyo.Set(initialize=fi, ordered=True)
        # model.f_to_bmps = pyo.Param(model.F, initialize=fi_dict_ikeys)

        # *************************
        #  IMMUTABLE PARAMETERS
        # *************************
        model.tau = pyo.Param(model.BMPS,
                              doc="""cost per acre of BMP b ($)""",
                              within=pyo.NonNegativeReals,
                              initialize=dataplate.tau)

        model.eta = pyo.Param(model.BMPS,
                              model.LRSEGS,
                              model.LOADSRCS,
                              model.PLTNTS,
                              doc='effectiveness per acre of BMP b (unitless)',
                              within=pyo.NonNegativeReals,
                              initialize={(k[0], k[1], k[2], k[3]): v
                                          for k, v in dataplate.eta.items()})

        model.phi = pyo.Param(model.PARCELS,
                              model.PLTNTS,
                              doc='base nutrient load per load source',
                              within=pyo.NonNegativeReals,
                              initialize={(k[0], k[1], k[2], k[3]): v
                                          for k, v in dataplate.phi.items()},
                              mutable=True)

        model.alpha = pyo.Param(model.PARCELS,
                                doc='total acres available in an lrseg/loadsource/agency',
                                within=pyo.NonNegativeReals,
                                mutable=True,
                                initialize={k: v for k, v in dataplate.alpha.items()})

        # vvvv TODO: DO THESE feasible assignment calculations vvvv
        lowerecalc = {}
        def lowere_rule(mdl, f, l):
            temp_val = pyo.prod([1 - mdl.eta[(bmp_tuple, l)]
                                 for bmp_tuple in fi_dict_fkeys[f]])
            # lowerecalc[(fi_dict_fkeys[(b1, b2)], lrsegid)] =
            return temp_val
        model.lowere = pyo.Param(model.F,
                                 model.LRSEGS,
                                 doc='overall pass through of a feasible assignment (unitless)',
                                 within=pyo.NonNegativeReals,
                                 rule=lowere_rule)

        lowerccalc = {}
        for (b1, b2) in feasible_assignments:
            lrsegid = 'lrseg1'
            lowerccalc[(fi_dict_fkeys[(b1, b2)], lrsegid)] = model.c[b1] + model.c[b2]
        model.lowerc = pyo.Param(model.F,
                                 model.LRSEGS,
                                 doc='overall cost of a feasible assignment (unitless)',
                                 within=pyo.NonNegativeReals,
                                 initialize=lowerccalc)

        # *************************
        #  MUTABLE PARAMETERS
        # *************************
        model.target_load_param = pyo.Param(model.PLTNTS,
                                            initialize={p: target_load[p]
                                                        for p in dataplate.PLTNTS},
                                            mutable=True)

        # *************************
        # VARIABLES
        # *************************
        def _bounds_rule(m, b, k1, k2, k3):
            return 0, dataplate.alpha[k1, k2, k3]
        model.x = pyo.Var(model.BMPS,
                          model.PARCELS,
                          domain=pyo.NonNegativeReals,
                          bounds=_bounds_rule,
                          doc='Amount of each BMP to implement.')

        # model.x = pyo.Var(model.BMPS,
        #                   model.LRSEGS,
        #                   model.LOADSRCS,
        #                   domain=pyo.NonNegativeReals,
        #                   doc='Amount of each BMP to implement.')

        return model