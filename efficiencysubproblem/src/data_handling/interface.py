from .datahandler_base import DataHandlerBase
from .dataloader_constraint_mixins import DataCostConstraintMixin, \
    DataLoadConstraintAtCountyLevelMixin, DataLoadConstraintAtLrsegLevelMixin
from .dataloader_geography_mixins import DataCountyGeoentitiesMixin, DataLrsegGeoentitiesMixin


def get_loaded_data_handler(objectivetype, geoscale, geoentities, savedata2file=False):
    """ This function figures out how to create the desired datahandler type """
    if objectivetype == 'costmin':
        if geoscale == 'lrseg':
            datahandler = DataHandlerLrsegWithLoadReductionConstraint(savedata2file=savedata2file, geoentities=geoentities)
        elif geoscale == 'county':
            datahandler = DataHandlerCountyWithLoadReductionConstraint(savedata2file=savedata2file, geoentities=geoentities)
        else:
            raise ValueError('unrecognized "geoscale"')

    elif objectivetype == 'loadreductionmax':
        if geoscale == 'lrseg':
            datahandler = DataHandlerLrsegWithCostConstraint(savedata2file=savedata2file, geoentities=geoentities)
        elif geoscale == 'county':
            datahandler = DataHandlerCountyWithCostConstraint(savedata2file=savedata2file, geoentities=geoentities)
        else:
            raise ValueError('unrecognized "geoscale"')

    else:
        raise ValueError('unrecognized objectivetype')

    return datahandler


""" Different DataHandler classes inherit from different Mixin combinations """


class DataHandlerLrsegWithLoadReductionConstraint(DataLoadConstraintAtLrsegLevelMixin,
                                                  DataLrsegGeoentitiesMixin,
                                                  DataHandlerBase):
    def __init__(self, savedata2file=None, geoentities=None):

        self.tau = None

        DataHandlerBase.__init__(self, save2file=savedata2file, geolist=geoentities)


class DataHandlerCountyWithLoadReductionConstraint(DataLoadConstraintAtCountyLevelMixin,
                                                   DataCountyGeoentitiesMixin,
                                                   DataHandlerBase):
    def __init__(self, savedata2file=None, geoentities=None):

        self.countysetlist = []
        self.countysetidlist = []
        self.COUNTIES = []
        self.CNTYLRSEGLINKS = []

        self.tau = None

        DataHandlerBase.__init__(self, save2file=savedata2file, geolist=geoentities)


class DataHandlerLrsegWithCostConstraint(DataCostConstraintMixin,
                                         DataLrsegGeoentitiesMixin,
                                         DataHandlerBase):
    def __init__(self, savedata2file=None, geoentities=None):
        DataHandlerBase.__init__(self, save2file=savedata2file, geolist=geoentities)


class DataHandlerCountyWithCostConstraint(DataCostConstraintMixin,
                                          DataCountyGeoentitiesMixin,
                                          DataHandlerBase):
    def __init__(self, savedata2file=None, geoentities=None):

        self.countysetlist = []
        self.countysetidlist = []
        self.COUNTIES = []
        self.CNTYLRSEGLINKS = []

        DataHandlerBase.__init__(self, save2file=savedata2file, geolist=geoentities)