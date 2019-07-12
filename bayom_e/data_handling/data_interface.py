from .datahandler_base import DataHandlerBase
from .dataloader_geography_mixins import DataCountyGeoentitiesMixin, DataLrsegGeoentitiesMixin
from .dataplate import NLP_DataPlate

import math
import time
import string
import random
import numpy as np
from scipy.stats import skewnorm
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


def random_list_of_names(n, name_length=3, chars=string.ascii_uppercase) -> list:
    # A list of random names is generated.
    name_list = []
    for i in range(n):
        while True:  # generate a new name until we find one not already in the list.
            newword = word_generator(size=name_length, chars=chars)
            if newword not in name_list:  # don't add a duplicate
                name_list.append(newword)
                break
    return name_list


def skewed_dist(max_value=10, min_value=0, num_values=10000, skewness=5, integers=False):
    """ generate skewed distribution """
    # Negative skewness values are left skewed (long right tail), positive values are right skewed (left tail).
    skewness_val = skewness
    desired_range = max_value - min_value

    random_list = skewnorm.rvs(a=skewness_val, loc=max_value, size=num_values)
    # The list is shifted so that the minimum value is equal to zero (+ an optional min_value).
    random_list = random_list - min(random_list)
    # Values are standardized to be between 0 and 1.
    random_list = random_list / max(random_list)
    # The standardized values are rescaled to the desired minimum - maximum range
    random_list = (random_list * desired_range) + min_value

    if integers:
        random_list = np.round(random_list, 0).astype(int)

    return list(random_list)

def make_random_bmp_groupings(pollutants_list, lrseg_list, loadsrc_list,
                              num_bmps=8, num_bmpgroups=3, mingrpsize=1, maxgrpsize=10):
    """

    Args:
        num_bmps (int):
        num_bmpgroups (int):
        mingrpsize (int):
        maxgrpsize (int):

    Return:
        bmp_list (list):
        grp_sizes (dict):
        bmpgroups_list (list):

    """
    # We first check that the specified group parameters are feasible.
    assert mingrpsize <= maxgrpsize
    if math.floor(num_bmps / num_bmpgroups) < mingrpsize:
        raise ValueError(f"{num_bmps} BMPs cannot be distributed among {num_bmpgroups} groups "
                         f"while maintaining groups larger than the specified minimum size of {mingrpsize}")
    if math.ceil(num_bmps / num_bmpgroups) > maxgrpsize:
        raise ValueError(f"the specified maximum group size of {maxgrpsize} will be exceeded "
                         f"by distributed {num_bmps} BMPs among {num_bmpgroups} groups")

    # A list of random bmp names is generated [of length 'num_bmps'].
    bmp_list = random_list_of_names(n=num_bmps, name_length=6, chars=string.ascii_uppercase + string.ascii_lowercase)

    # Random costs are generated for each bmp.
    tau_dict = {b: random.randint(0, 1000) for b in bmp_list}

    # Random effectiveness values are generated for each bmp.
    eta_dict = {}
    for b in bmp_list:
        for p in pollutants_list:
            for l in lrseg_list:
                for u in loadsrc_list:
                    eta_dict[(b, p, l, u)] = round(random.random(), 2)

    """ The sizes for each group are determined randomly. 
    """
    # generate skewed distribution
    random_list = skewed_dist(max_value=maxgrpsize, min_value=0, num_values=10000, skewness=5, integers=True)
    # The minimum group size is used as a starting point to which we will add.
    grp_sizes = {i: mingrpsize for i in range(0, num_bmpgroups)}
    # Groups are randomly selected to have their size incrementally increased by 1.
    #   (while not exceeding max group size, and up to the total number of BMPs)
    remainingtoadd = num_bmps - (mingrpsize * num_bmpgroups)
    timeout = time.time() + 60 * 2  # 2 minutes from now
    while remainingtoadd > 0:
        # grptoaddto = random.randint(0, num_bmpgroups - 1)  # this gives an approximate uniform distribution
        # grptoaddto = np.random.choice(num_bmpgroups, size=1, p=prob)[0]  # this can be used to choose groups unevenly
        grptoaddto = np.random.choice(num_bmpgroups, size=1)[0]
        if grp_sizes[grptoaddto] <= maxgrpsize:
            howmanytoaddtogroup = np.random.choice(random_list, size=1)[0]
            if ((remainingtoadd - howmanytoaddtogroup) >= 0) and \
                    ((grp_sizes[grptoaddto] + howmanytoaddtogroup) <= maxgrpsize):
                grp_sizes[grptoaddto] += howmanytoaddtogroup
                remainingtoadd -= howmanytoaddtogroup
                # print(f"*added {howmanytoaddtogroup} to group {grptoaddto}")
        if time.time() > timeout:
            raise ValueError(f"dataplate bmpgroup random generator timed out after {timeout} seconds")

    # BMPs are assigned to groups using the specified sizes.
    bmpgroups_list = []
    bmplistforpopping = bmp_list.copy()
    for g_index, g_size in grp_sizes.items():
        thisgrpsbmps = []
        for i in range(g_size):
            thisgrpsbmps.append(bmplistforpopping.pop())
        bmpgroups_list.append(Group(index=g_index, size=len(thisgrpsbmps), bmps=thisgrpsbmps))

    return bmp_list, grp_sizes, bmpgroups_list, tau_dict, eta_dict


def randomly_assign_grps_to_loadsources(loadsrc_list, bmpgroups_list, minloadsrcgrpingsize=1,
                                        maxloadsrcgrpingsize=4):
    bmpgrouplist = bmpgroups_list.copy()
    num_bmpgroups = len(bmpgrouplist)
    assert num_bmpgroups > 0
    if num_bmpgroups < maxloadsrcgrpingsize:
        raise ValueError(f"the specified maximum # of groups for a load source <{maxloadsrcgrpingsize}> "
                         f"can never be met with only {num_bmpgroups} BMP groups.  "
                         f"It is recommended to lower maxloadsrcgrpingsize to {num_bmpgroups}.")

    # The sizes for each load source grouping are determined randomly.
    random_list = skewed_dist(max_value=maxloadsrcgrpingsize+1, min_value=minloadsrcgrpingsize,
                              num_values=10000, skewness=5, integers=True)
    loadsrc_sizes = np.random.choice(random_list, size=len(loadsrc_list)).tolist()

    # BMPGRPS are assigned to load sources using the specified sizes.
    grploadsrc_dict = {}
    for ls_index, ls_size in enumerate(loadsrc_sizes):
        thisloadsourcesgrps = []
        for i in range(ls_size):
            while True:  # pick a random bmp group until we find one not already in the list.
                # pop from the bmpgrouplist itself, until it's depleted...
                # that way we've put each bmpgroup into at least one load source
                if bmpgrouplist:
                    bmpgrpchoicelistidx = random.randint(0, len(bmpgrouplist) - 1)
                    bmpgrpchoiceidx = bmpgrouplist[bmpgrpchoicelistidx].index
                    if bmpgrpchoiceidx not in thisloadsourcesgrps:
                        thisloadsourcesgrps.append(bmpgrouplist.pop(bmpgrpchoicelistidx).index)
                        break
                else:
                    # once depleted, keep putting random bmps in loadsources until desired loadsource sizes are met
                    bmpgrpchoicelistidx = random.randint(0, num_bmpgroups - 1)
                    if bmpgrpchoicelistidx not in thisloadsourcesgrps:
                        thisloadsourcesgrps.append(bmpgrpchoicelistidx)
                        break
        grploadsrc_dict[loadsrc_list[ls_index]] = thisloadsourcesgrps

    return loadsrc_sizes, grploadsrc_dict


def get_random_dataplate(name='nlp', num_lrsegs=1,
                         num_bmps=8, num_bmpgroups=3, num_loadsources=2,
                         minbmpgrpsize=1, maxbmpgrpsize=10,
                         minloadsrcgrpingsize=1, maxloadsrcgrpingsize=4,
                         savedata2file=False):

    pollutants_list = ['N']
    lrseg_list = random_list_of_names(n=num_lrsegs, name_length=19, chars=string.ascii_uppercase + string.digits)
    loadsrc_list = random_list_of_names(n=num_loadsources, name_length=3, chars=string.ascii_lowercase)
    agency_list = ['nonfed']

    bmplist, grpsizes, bmpgrplist, tau_dict, eta_dict = make_random_bmp_groupings(pollutants_list=pollutants_list,
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
    parcel_list = []
    for l in lrseg_list:
        for u in loadsrc_list:
            for h in agency_list:
                parcel_list.append((l, u, h))
                alpha_dict[(l, u, h)] = random.randint(0, 10000)
                for p in pollutants_list:
                    phi_dict[(l, u, h, p)] = random.randint(0, 2000)

    if name == 'nlp':
        return NLP_DataPlate(PLTNTS=['N'],
                             LRSEGS=lrseg_list,
                             LOADSRCS=loadsrc_list,
                             AGENCIES=agency_list,
                             PARCELS=parcel_list,
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
                  savedata2file=False):
    dh = get_loaded_data_handler_no_objective(geoscale, geoentities,
                                              savedata2file=savedata2file, baseloadingfilename=baseloadingfilename)

    if name == 'nlp':
        return NLP_DataPlate(PLTNTS=dh.PLTNTS,
                             LRSEGS=dh.LRSEGS,
                             LOADSRCS=dh.LOADSRCS,
                             AGENCIES=dh.AGENCIES,
                             PARCELS=dh.PARCELS,
                             BMPS=dh.BMPS,
                             BMPGRPS=dh.BMPGRPS,
                             BMPGRPING=dh.BMPGRPING,
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
