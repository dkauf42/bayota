""" Build a NLP variant of the Efficiency BMP model (A subclass of ModelBuilder)
"""

# Generic/Built-in
import logging
from typing import Dict

# Computation
import pyomo.environ as pyo

# BAYOTA
from bayom_e.model_handling.builders.modelbuilder import ModelBuilder

default_logger = logging.getLogger(__name__)


class NonlinearVariant(ModelBuilder):
    """ Used to build an NLP variant of the Efficiency BMP model (A subclass of ModelBuilder)
    """

    def __init__(self, logger=default_logger):
        """ Please see help(NonlinearVariant) for more info """
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

        # BMPS
        model.BMPS = pyo.Set(initialize=dataplate.BMPS, ordered=True)
        model.BMPGRPS = pyo.Set(initialize=dataplate.BMPGRPS)

        # BMPs in each BMPGRP
        self.create_2dim_set_component(model, dataplate.BMPGRPING, 'BMPGRPING')

        # BMPs in each LOADSRC
        self.create_2dim_set_component(model, dataplate.BMPSRCLINKS, 'BMPSRCLINKS')

        # BMPGRPs in each LOADSRC
        self.create_2dim_set_component(model, dataplate.BMPGRPSRCLINKS, 'BMPGRPSRCLINKS')

        # *************************
        # IMMUTABLE PARAMETERS
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

        return model
