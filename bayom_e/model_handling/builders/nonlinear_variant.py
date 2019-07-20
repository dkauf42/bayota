import pyomo.environ as pyo

from bayom_e.model_handling.builders.modelbuilder import ModelBuilder

import logging
default_logger = logging.getLogger(__name__)


class NonlinearVariant(ModelBuilder):
    """ Used to build an NLP variant of the Efficiency BMP model (A subclass of ModelBuilder)
    """

    def __init__(self, logger=default_logger):
        """ Please see help(NonlinearVariant) for more info """
        ModelBuilder.__init__(self, logger=logger)

    def build_skeleton(self, dataplate, geoscale, target_load=1) -> pyo.ConcreteModel:
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
        # if geoscale == 'lrseg':
        #     model.LRSEGS = pyo.Set(initialize=dataplate.LRSEGS)
        # elif geoscale == 'county':
        #     model.COUNTIES = pyo.Set(initialize=dataplate.COUNTIES)
        #     model.LRSEGS = pyo.Set(initialize=dataplate.LRSEGS)
        #     model.CNTYLRSEGLINKS = pyo.Set(initialize=dataplate.CNTYLRSEGLINKS, dimen=2)
        # else:
        #     raise ValueError('unrecognized geoscale <%s>' % geoscale)
        model.LOADSRCS = pyo.Set(initialize=dataplate.LOADSRCS)
        model.AGENCIES = pyo.Set(initialize=dataplate.AGENCIES)
        model.PARCELS = pyo.Set(initialize=dataplate.PARCELS, within=model.LRSEGS*model.LOADSRCS*model.AGENCIES)

        # BMPS
        model.BMPS = pyo.Set(initialize=dataplate.BMPS, ordered=True)
        model.BMPGRPS = pyo.Set(initialize=dataplate.BMPGRPS)

        # BMPs in each BMPGRP
        if isinstance(dataplate.BMPGRPING, dict):
            temp_list = []
            for grp, bmps in dataplate.BMPGRPING.items():
                for b in bmps:
                    temp_list.append((grp, b))
            model.BMPGRPING = pyo.Set(initialize=temp_list, dimen=2)
        else:
            model.BMPGRPING = pyo.Set(initialize=dataplate.BMPGRPING, dimen=2)

        # BMPs in each LOADSRC
        if isinstance(dataplate.BMPSRCLINKS, dict):
            temp_list = []
            for ldsrc, bmps in dataplate.BMPSRCLINKS.items():
                for b in bmps:
                    temp_list.append((b, ldsrc))
            model.BMPSRCLINKS = pyo.Set(initialize=temp_list, dimen=2)
        else:
            model.BMPSRCLINKS = pyo.Set(initialize=dataplate.BMPSRCLINKS, dimen=2)

        # BMPGRPs in each LOADSRC
        if isinstance(dataplate.BMPGRPSRCLINKS, dict):
            temp_list = []
            for ldsrc, grps in dataplate.BMPGRPSRCLINKS.items():
                for g in grps:
                    temp_list.append((g, ldsrc))
            model.BMPGRPSRCLINKS = pyo.Set(initialize=temp_list, dimen=2)
        else:
            model.BMPGRPSRCLINKS = pyo.Set(initialize=dataplate.BMPGRPSRCLINKS, dimen=2)

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

        # model.phi = pyo.Param(model.LRSEGS,
        #                       model.LOADSRCS,
        #                       doc='base nutrient load per load source',
        #                       within=pyo.NonNegativeReals,
        #                       initialize={(k[0], k[1]): v
        #                                   for k, v in dataplate.phi.items()
        #                                   if k[2] == 'N'},
        #                       mutable=True)

        model.alpha = pyo.Param(model.PARCELS,
                                doc='total acres available in an lrseg/loadsource/agency',
                                within=pyo.NonNegativeReals,
                                mutable=True,
                                initialize={k: v for k, v in dataplate.alpha.items()})

        # model.alpha = pyo.Param(model.LRSEGS,
        #                         model.LOADSRCS,
        #                         doc='total acres available in an lrseg/load source',
        #                         within=pyo.NonNegativeReals,
        #                         mutable=True,
        #                         initialize={k: v for k, v in dataplate.alpha.items()})

        # *************************
        #  MUTABLE PARAMETERS
        # *************************
        model.target_load_param = pyo.Param(initialize=target_load,
                                            mutable=True)

        # *************************
        # VARIABLES
        # *************************
        model.x = pyo.Var(model.BMPS,
                          model.PARCELS,
                          domain=pyo.NonNegativeReals,
                          doc='Amount of each BMP to implement.')

        # model.x = pyo.Var(model.BMPS,
        #                   model.LRSEGS,
        #                   model.LOADSRCS,
        #                   domain=pyo.NonNegativeReals,
        #                   doc='Amount of each BMP to implement.')

        return model
