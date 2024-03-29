""" Interface for retrieving DataPlate and DataHandler objects.
"""

# Generic/Built-in
import string

# BAYOTA data handling
from .randomizer import random_list_of_names, make_random_bmp_groupings, \
    randomly_assign_grps_to_loadsources, random_bmp_parameters, random_parcel_parameters
from .datahandler_base import DataHandlerBase
from .dataloader_geography_mixins import DataCountyGeoentitiesMixin, DataLrsegGeoentitiesMixin
from .dataplate import NLP_DataPlate


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
    agency_list = ['nonfed']

    bmplist, grpsizes, bmpgrplist = make_random_bmp_groupings(num_bmps=num_bmps,
                                                              num_bmpgroups=num_bmpgroups,
                                                              mingrpsize=minbmpgrpsize,
                                                              maxgrpsize=maxbmpgrpsize)
    tau_dict, eta_dict = random_bmp_parameters(bmplist, pollutants_list, lrseg_list, loadsrc_list,
                                               cost_upper_limit=1000)

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

    alpha_dict, phi_dict, parcel_list = random_parcel_parameters(lrseg_list, loadsrc_list, agency_list, pollutants_list)

    if name == 'nlp':
        return NLP_DataPlate(PLTNTS=pollutants_list,
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

    def __repr__(self):
        obj_attributes = sorted([k for k in self.__dict__.keys()
                                 if not k.startswith('_')])
        n_lrsegs = len(self.LRSEGS)
        n_parcels = len(self.PARCELS)

        strrep = f"DataHandlerLrseg: \n" \
                 f"\t- includes <{n_lrsegs}> land river {'segment' if n_lrsegs==1 else 'segments'}\n" \
                 f"\t- includes <{n_parcels}> {'parcel' if n_parcels==1 else 'parcels'}\n" \
                 f"\n" \
                 f"\t all attributes:%s" % '\n\t\t\t'.join(obj_attributes)

        return strrep


class DataHandlerCounty(DataCountyGeoentitiesMixin, DataHandlerBase):
    def __init__(self, save2file=True, geolist=None, baseloadingfilename=''):

        self.countysetlist = []
        self.countysetidlist = []
        self.COUNTIES = []
        self.CNTYLRSEGLINKS = []

        DataHandlerBase.__init__(self, save2file=save2file, geolist=geolist, baseloadingfilename=baseloadingfilename)

    def __repr__(self):
        obj_attributes = sorted([k for k in self.__dict__.keys()
                                 if not k.startswith('_')])
        n_counties = len(self.COUNTIES)
        n_lrsegs = len(self.LRSEGS)
        n_parcels = len(self.PARCELS)

        strrep = f"DataHandlerCounty: \n" \
                 f"\t- includes <{n_counties}> {'county' if n_counties==1 else 'counties'}\n" \
                 f"\t- includes <{n_lrsegs}> land river {'segment' if n_lrsegs==1 else 'segments'}\n" \
                 f"\t- includes <{n_parcels}> {'parcel' if n_parcels==1 else 'parcels'}\n" \
                 f"\n" \
                 f"\t all attributes:%s" % '\n\t\t\t'.join(obj_attributes)

        return strrep
