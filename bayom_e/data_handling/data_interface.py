"""
Interface for retrieving DataPlate and DataHandler objects.
"""
from .randomizer import random_list_of_names, random_bmp_groupings, randomly_assign_grps_to_loadsources
from .datahandler_base import DataHandlerBase
from .dataloader_geography_mixins import DataCountyGeoentitiesMixin, DataLrsegGeoentitiesMixin
from .dataplate import NLP_DataPlate

import string
import random
from collections import namedtuple

Group = namedtuple("Group", ['index', 'size', 'bmps'])
LoadSrc = namedtuple("LoadSrc", ['index', 'name', 'size', 'bmpgroups'])


def get_random_dataplate(name='nlp', num_lrsegs=1,
                         num_bmps=8, num_bmpgroups=3, num_loadsources=2,
                         minbmpgrpsize=1, maxbmpgrpsize=10,
                         minloadsrcgrpingsize=1, maxloadsrcgrpingsize=4,
                         savedata2file=False) -> NLP_DataPlate:
    """ Create a random dataplate object.

    Args:
        name:
        num_lrsegs:
        num_bmps:
        num_bmpgroups:
        num_loadsources:
        minbmpgrpsize:
        maxbmpgrpsize:
        minloadsrcgrpingsize:
        maxloadsrcgrpingsize:
        savedata2file:

    Returns:

    """

    pollutants_list = ['N']
    lrseg_list = random_list_of_names(n=num_lrsegs, name_length=19, chars=string.ascii_uppercase + string.digits)
    loadsrc_list = random_list_of_names(n=num_loadsources, name_length=3, chars=string.ascii_lowercase)

    bmplist, grpsizes, bmpgrplist, tau_dict, eta_dict = random_bmp_groupings(pollutants_list=pollutants_list,
                                                                             lrseg_list=lrseg_list,
                                                                             loadsrc_list=loadsrc_list,
                                                                             num_bmps=num_bmps,
                                                                             num_bmpgroups=num_bmpgroups,
                                                                             mingrpsize=minbmpgrpsize,
                                                                             maxgrpsize=maxbmpgrpsize)
    # print(f"bmp group sizes are {grpsizes}.  sum={sum([s for _, s in grpsizes.items()])}")
    # print('\n')

    loadsrc_sizes, grploadsrc_dict = randomly_assign_grps_to_loadsources(loadsrc_list=loadsrc_list,
                                                                         bmpgroups_list=bmpgrplist,
                                                                         minloadsrcgrpingsize=minloadsrcgrpingsize,
                                                                         maxloadsrcgrpingsize=maxloadsrcgrpingsize)
    # print(f"load source sizes are {loadsrc_sizes}.  sum={sum(loadsrc_sizes)}")
    # print(grploadsrc_list)

    # Each load source is assigned a list of bmps according to the bmpgroup(s) already associated with the loadsource.
    bmpsrc_dict = {}
    for ls, grps in grploadsrc_dict.items():
        bmpsrc_list = []
        for g in grps:
            for b in bmpgrplist[g].bmps:
                bmpsrc_list.append(b)
        bmpsrc_dict[ls] = bmpsrc_list

    # Random acreages (alpha) and base loadings (phi) are generated
    alpha_dict = {}
    phi_dict = {}
    for l in lrseg_list:
        for u in loadsrc_list:
            alpha_dict[(l, u)] = random.randint(0, 10000)
            for p in pollutants_list:
                phi_dict[(l, u, p)] = random.randint(0, 2000)

    if name == 'nlp':
        return NLP_DataPlate(PLTNTS=pollutants_list,
                             LRSEGS=lrseg_list,
                             LOADSRCS=loadsrc_list,
                             BMPS=bmplist,
                             BMPGRPS=[g.index for g in bmpgrplist],
                             BMPGRPING={g.index: g.bmps for g in bmpgrplist},
                             BMPSRCLINKS=bmpsrc_dict,
                             BMPGRPSRCLINKS=grploadsrc_dict,
                             theta=1,
                             alpha=alpha_dict,
                             phi=phi_dict,
                             tau=tau_dict,
                             eta=eta_dict)


def get_dataplate(geoscale, geoentities, baseloadingfilename, name='nlp',
                  savedata2file=False) -> NLP_DataPlate:
    """ Create a dataplate object for a given geography.

    Args:
        geoscale:
        geoentities:
        baseloadingfilename:
        name:
        savedata2file:

    Returns:

    """
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


def get_loaded_data_handler_no_objective(geoscale, geoentities,
                                         savedata2file=False, baseloadingfilename=''):
    """ Create a DataHandler object for a given geography.

    Args:
        geoscale:
        geoentities:
        savedata2file:
        baseloadingfilename:

    Returns:

    """
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
