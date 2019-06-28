from .datahandler_base import DataHandlerBase
from .dataloader_geography_mixins import DataCountyGeoentitiesMixin, DataLrsegGeoentitiesMixin


def get_loaded_data_handler_no_objective(geoscale, geoentities, savedata2file=False, baseloadingfilename=''):
    if geoscale == 'lrseg':
        datahandler = DataHandlerLrseg(save2file=savedata2file, geolist=geoentities, baseloadingfilename=baseloadingfilename)
    elif geoscale == 'county':
        datahandler = DataHandlerCounty(save2file=savedata2file, geolist=geoentities, baseloadingfilename=baseloadingfilename)
    else:
        raise ValueError('<%s> is an unrecognized "geoscale".' % geoscale)

    return datahandler


class DataHandlerLrseg(DataLrsegGeoentitiesMixin, DataHandlerBase):
    def __init__(self, save2file=True, geolist=None, baseloadingfilename=''):
        DataHandlerBase.__init__(self, save2file=save2file, geolist=geolist, baseloadingfilename=baseloadingfilename)


class DataHandlerCounty(DataCountyGeoentitiesMixin, DataHandlerBase):
    def __init__(self, save2file=True, geolist=None, baseloadingfilename=''):

        self.countysetlist = []
        self.countysetidlist = []
        self.COUNTIES = []
        self.CNTYLRSEGLINKS = []

        DataHandlerBase.__init__(self, save2file=save2file, geolist=geolist, baseloadingfilename=baseloadingfilename)
