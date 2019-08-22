import pyomo.environ as pyo

from bayom_e.model_handling.builders.modelbuilder import ModelBuilder

import logging
default_logger = logging.getLogger(__name__)


class LinearVariant(ModelBuilder):
    """ Used to build a LP variant of the Efficiency BMP model (A subclass of ModelBuilder)
    """

    def __init__(self, logger=default_logger):
        """ Please see help(LinearVariant) for more info """
        ModelBuilder.__init__(self, logger=logger)
