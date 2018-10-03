from .dataloader_base import DataLoaderBase
from .dataloader_costconstraint_mixin import CostConstraintMixin
from .dataloader_loadconstraint_mixin import LoadConstraintMixin
from .dataloader_county_mixin import CountyMixin
from .dataloader_lrseg_mixin import LrsegMixin


class CountyWithCostConstraint(CostConstraintMixin, CountyMixin, DataLoaderBase):
    def __init__(self, save2file=None, geolist=None):
        self.countysetlist = []
        self.countysetidlist = []
        self.COUNTIES = []
        self.CNTYLRSEGLINKS = []

        # super constructor
        print('CountyWithCostConstraint.__init__()')
        DataLoaderBase.__init__(self, save2file=save2file, geolist=geolist)


class LrsegWithCostConstraint(CostConstraintMixin, LrsegMixin, DataLoaderBase):
    def __init__(self, save2file=None, geolist=None):
        # super constructor
        print('LrsegWithCostConstraint.__init__()')
        DataLoaderBase.__init__(self, save2file=save2file, geolist=geolist)


class LrsegWithLoadReductionConstraint(LoadConstraintMixin, LrsegMixin, DataLoaderBase):
    def __init__(self, save2file=None, geolist=None):
        self.tau = None

        # super constructor
        print('LrsegWithLoadReductionConstraint.__init__()')
        DataLoaderBase.__init__(self, save2file=save2file, geolist=geolist)


class CountyWithLoadReductionConstraint(LoadConstraintMixin, CountyMixin, DataLoaderBase):
    def __init__(self, save2file=None, geolist=None):
        self.countysetlist = []
        self.countysetidlist = []
        self.COUNTIES = []
        self.CNTYLRSEGLINKS = []

        self.tau = None

        # super constructor
        print('CountyWithLoadReductionConstraint.__init__()')
        DataLoaderBase.__init__(self, save2file=save2file, geolist=geolist)