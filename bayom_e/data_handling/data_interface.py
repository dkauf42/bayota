from .datahandler_base import DataHandlerBase
from .dataloader_geography_mixins import DataCountyGeoentitiesMixin, DataLrsegGeoentitiesMixin
from .dataplate import NLP_DataPlate

import math
import string
import random
import numpy as np
from collections import namedtuple

Group = namedtuple("Group", ['index', 'size', 'bmps'])
LoadSrc = namedtuple("LoadSrc", ['index', 'name', 'size', 'bmpgroups'])


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def word_generator(size=6, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


def random_ints_with_sum(n):
    """
    Generate positive random integers summing to `n`, sampled
    uniformly from the ordered integer partitions of `n`.
    """
    p = 0
    for _ in range(n - 1):
        p += 1
        if random.randrange(2):
            yield p
            p = 0
    yield p + 1


def get_dataplate(geoscale, geoentities, baseloadingfilename, name='nlp',
                  savedata2file=False):
    dh = get_loaded_data_handler_no_objective(geoscale, geoentities,
                                              savedata2file=savedata2file, baseloadingfilename=baseloadingfilename)

    if name == 'nlp':
        return NLP_DataPlate(PLTNTS=dh.PLTNTS,
                             LRSEGS=dh.LRSEGS,
                             BMPS=dh.BMPS,
                             BMPGRPS=dh.BMPGRPS,
                             BMPGRPING=dh.BMPGRPING,
                             LOADSRCS=dh.LOADSRCS,
                             BMPSRCLINKS=dh.BMPSRCLINKS,
                             BMPGRPSRCLINKS=dh.BMPGRPSRCLINKS,
                             theta=dh.Theta,
                             alpha=dh.alpha,
                             phi=dh.phi,
                             tau=dh.tau,
                             eta=dh.eta)


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
