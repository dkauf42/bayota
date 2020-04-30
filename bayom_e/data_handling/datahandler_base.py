""" Provide formatted/parsed/wrangled data for efficiency BMP models """

# Generic/Built-in
import os
import logging

# Computation
import numpy as np
import pandas as pd

# BAYOTA
from bayota_settings.base import get_model_instances_dir, get_raw_data_dir
from .bmp_exclusions import excluded_bmps_list
from castjeeves.jeeves import Jeeves

logger = logging.getLogger(__name__)


class DataHandlerBase:
    """Base Class for data loader classes - provides formatted/parsed/wrangled data for efficiency BMP models

    Attributes:
        save2file ():
        instdatadir ():
        PLTNTS (pd.DataFrame):
        LRSEGS (pd.DataFrame):
        BMPS (pd.DataFrame):
        BMPGRPS (pd.DataFrame):
        BMPGRPING (pd.DataFrame):
        LOADSRCS (pd.DataFrame):
        AGENCIES (pd.DataFrame):
        BMPSRCLINKS (pd.DataFrame):
        BMPGRPSRCLINKS (pd.DataFrame):
        tau (pd.DataFrame):
        eta (pd.DataFrame):
        Theta (pd.DataFrame):
        phi (pd.DataFrame):
        alpha (pd.DataFrame):
        lrsegsetlist (list):
        lrsegsetidlist (list):
        bmpsetlist (list):
        bmpsetidlist (list):
        loadsrcsetidlist (list):
        costsubtbl (pd.DataFrame):

    Args:
        save2file (bool): Defaults to True.
        geolist (list): The list of geographic entities for which to pull data. Defaults to None.
        baseloadingfilename (str):
        landchangemodelscenario (str):
        baseyear (int or str):

    """
    def __init__(self, save2file=True, geolist=None, baseloadingfilename='',
                 landchangemodelscenario='Historic Trends', baseyear='2010',
                 ImpBmpScenarioId=None):
        self._geolist = geolist

        logger.debug(locals())
        jeeves = Jeeves()

        # Save instance data to file?
        self.save2file = save2file
        self.instdatadir = get_model_instances_dir()

        """ Instance Specifiers """
        self._landchangemodelscenario = landchangemodelscenario  # typically 'Historic Trends' or "Current Zoning"
        self._baseyear = baseyear
        self._baseconditionid = jeeves.scenario.get_baseconditionid(landchangemodelscenario=self._landchangemodelscenario,
                                                                    baseyear=self._baseyear)
        self._costprofileid = 4

        # **********************************************************************
        # Load Source Data tables into memory
        # **********************************************************************

        """ Data tables for the set definitions """
        TblBmp = jeeves.source.TblBmp.copy()
        TblBmpGroup = jeeves.source.TblBmpGroup.copy()
        TblBmpLoadSourceGroup = jeeves.source.TblBmpLoadSourceGroup.copy()
        TblBmpType = jeeves.source.TblBmpLoadSourceGroup.copy()

        TblLoadSource = jeeves.source.TblLoadSource.copy()
        TblLoadSource['loadsource'] = TblLoadSource[
            'loadsource'].str.strip()  # There is an extra space after "Specialty Crop Low" that needs to be removed.

        TblLandRiverSegment = jeeves.source.TblLandRiverSegment.copy()

        TblGeography = jeeves.source.TblGeography.copy()
        TblGeographyLrSeg = jeeves.source.TblGeographyLrSeg.copy()
        TblGeographyType = jeeves.source.TblGeographyType.copy()

        """ Data tables for the parameter definitions """
        TblAgency = jeeves.source.TblAgency.copy()
        TblBmpEfficiency = jeeves.source.TblBmpEfficiency.copy()
        # Target load reductions ???  (set this ourselves??)
        TblLandUsePreBmp = jeeves.source.TblLandUsePreBmp.copy()
        TblCostBmpLand = jeeves.metadata_tables.TblCostBmpLand.copy()

        # **********************************************************************
        # Load auxiliary data into memory
        # **********************************************************************

        BaseConditionLoadsTbl = self._load_the_baseloading_data(baseloadingfilename, TblAgency, TblLoadSource)

        # Data table generated by separate python script, the set of load source *groups* where each load source *group* contains one and only one load source
        singlelsgrpdf = pd.read_csv(os.path.join(get_raw_data_dir(), 'single-ls_groups.csv'))

        # **********************************************************************
        # Initialize empty python variables for necessary Sets and Parameters
        # **********************************************************************

        # Data Sets
        self.PLTNTS = pd.DataFrame()
        self.LRSEGS = pd.DataFrame()
        self.LOADSRCS = pd.DataFrame()
        self.AGENCIES = pd.DataFrame()
        self.BMPS = pd.DataFrame()
        self.BMPGRPS = pd.DataFrame()
        self.BMPGRPING = pd.DataFrame()
        self.BMPSRCLINKS = pd.DataFrame()
        self.BMPGRPSRCLINKS = pd.DataFrame()

        # Data Parameters
        self.tau = pd.DataFrame()
        self.eta = pd.DataFrame()
        self.Theta = pd.DataFrame()
        self.phi = pd.DataFrame()
        # self.Theta = pd.DataFrame()
        # self.totalcostupperbound = pd.DataFrame()
        self.alpha = pd.DataFrame()

        # lists that will be populated by loading the Set data
        self.lrsegsetlist = []
        self.lrsegsetidlist = []
        # County setlists will also be included here for counties
        self.bmpsetlist = []
        self.bmpsetidlist = []
        self.loadsrcsetidlist = []

        # **********************************************************************
        # Populate the Sets and Parameters with appropriate data
        # **********************************************************************

        # Populate the data - SETS
        self._load_set_pollutants()

        self._load_set_geographies(jeeves, geolist=self._geolist)

        self._load_set_BMPs(jeeves, TblBmpLoadSourceGroup, TblBmpGroup)

        df_parcels = self._load_set_Parcels(TblLandUsePreBmp, TblLandRiverSegment,
                                            TblLoadSource, TblAgency, self._baseconditionid)

        self._load_set_LoadSources(TblLandUsePreBmp, singlelsgrpdf, self._baseconditionid)
        self._load_set_Agencies(TblLandUsePreBmp, TblAgency, self._baseconditionid)
        self._load_set_BmpLoadSourceAssociations(TblBmp, TblBmpEfficiency, TblBmpGroup,
                                                 TblBmpLoadSourceGroup, TblLoadSource, singlelsgrpdf)

        self.costsubtbl = pd.DataFrame()

        # Populate the data - PARAMETERS
        self._load_param_CostPerAcreOfBmps(TblBmp, TblCostBmpLand, self._costprofileid)
        self._load_param_EffectivenessOfBmps(TblBmp, TblBmpEfficiency, TblLandRiverSegment, TblLoadSource)

        self._load_constraint()

        self._load_param_PhiBaseLoadingRates(TblLandRiverSegment, TblGeography, TblGeographyType,
                                             TblGeographyLrSeg, TblLoadSource, BaseConditionLoadsTbl,
                                             TblAgency)
        self._load_param_TotalAcresAvailableForLoadSources(TblLandRiverSegment, TblLoadSource,
                                                           TblLandUsePreBmp, TblAgency, self._baseconditionid)

        logger.info('LRsegs loaded: %s' % self.lrsegsetlist)

    def __repr__(self):
        obj_attributes = sorted([k for k in self.__dict__.keys()
                                 if not k.startswith('_')])

        strrep = f"DATAHANDLER: \n" \
                 f"\t- for the baseconditionid: <{self._baseconditionid}>\n" \
                 f"\t- for the costprofileid: <{self._costprofileid}>\n" \
                 f"\t- for the geolist: <{self._geolist}>\n" \
                 f"\t- for the agencies: <{self.agencyid}>\n" \
                 f"\t- includes <{len(self.lrsegsetlist)}> land river segments\n" \
                 f"\n" \
                 f"\t all attributes:%s" % '\n\t\t\t'.join(obj_attributes)

        return strrep

    def _load_the_baseloading_data(self, baseloadingfilename, TblAgency, TblLoadSource):
        """ Load baseloading data from a file

        'baseloadingfilename' e.g. could be '2010NoActionLoads.csv'

        """
        # Make sure this base loading file has sufficient precision, we had an error caused by precision issues
        BaseConditionLoadsTbl = pd.read_csv(os.path.join(get_raw_data_dir(), baseloadingfilename))

        BaseConditionLoadsTbl.replace({'Agency': {'State Highway Administration': 'MD State Highway Administration',
                                                  'State': 'MD State'}}, inplace=True)

        def compare_sets(a, b, typename) -> str:
            msg = ''
            if not (a == b):
                amb = a - b
                bma = b - a
                if amb:
                    msg += f"{typename} {amb} are in the base loading table but not in the source table\n"
                if bma:
                    msg += f"{typename}s {bma} are in the source table but not in the base loading table\n"
            return msg

        # Do a simple check of the base load table
        errormessage = ''
        errormessage += compare_sets(set(BaseConditionLoadsTbl['Agency']),
                                    set(TblAgency['agencyfullname']), typename='agency(ies)')
        errormessage += compare_sets(set(BaseConditionLoadsTbl['LoadSource']),
                                    set(TblLoadSource['loadsource']), typename='load source(s)')
        if errormessage:
            raise ValueError(errormessage)

        return BaseConditionLoadsTbl

    def _load_constraint(self):
        """ overridden in the Mixins """
        pass

    def _load_set_pollutants(self):
        """ Pollutants """
        self.pltntslist = ['N', 'P', 'S']
        self.PLTNTS = self.pltntslist
        if self.save2file:
            pd.DataFrame(self.pltntslist, columns=['PLTNTS']).to_csv(os.path.join(self.instdatadir, 'data_PLTNTS.tab'), sep=' ', index=False)

    def _load_set_geographies(self, jeeves, geolist=None):
        """ overridden in the Mixins """
        pass

    def _load_set_lrsegs_from_lrseg_list(self, jeeves, lrsegs_list):
        """ Land River Segments """
        if not lrsegs_list:
            # lrsegs_list = ['N51133RL0_6450_0000']
            # lrsegs_list = ['N42071SL2_2410_2700']
            lrsegs_list = ['N42071SL2_2410_2700']

        # Land river segments that don't have any acres (are "non-physical land-river segments") are removed.
        # ...for example, N24031PL0_5390_0000 has zero acres and only represents wastewater loads
        totalacres = jeeves.lrseg.totalacres_for(lrsegnames=lrsegs_list)
        lrsegs_list = [a for a, b in zip(lrsegs_list, totalacres) if b != 0]

        # The list of land river segments is saved as object attributes.
        self.lrsegsetlist = lrsegs_list.copy()
        self.lrsegsetidlist = jeeves.geo.lrsegids_from(lrsegnames=lrsegs_list)

        if not self.lrsegsetidlist:
            raise ValueError('No LRSEGS found matching the input list')

        self.LRSEGS = lrsegs_list
        if self.save2file:
            pd.DataFrame(lrsegs_list, columns=['LRSEGS']).to_csv(os.path.join(self.instdatadir, 'data_LRSEGS.tab'), sep=' ', index=False)

    def _load_set_BMPs(self, jeeves, TblBmpLoadSourceGroup, TblBmpGroup):
        """ BMPs """
        # Get efficiency type id, and then restrict BMPs by:
        #  - Only include b if it's an 'efficiency' BMP
        #  - Only include b if it has a load source group on which it can be implemented
        # efftypeid = TblBmpType[TblBmpType['bmptype'] == 'Efficiency']['bmptypeid'].tolist()[0]
        # bmpsdf = TblBmp[TblBmp['bmptypeid'] == efftypeid]

        # Efficiency bmps are retrieved as a dataframe, and then they are restricted by:
        #  - Only include b if it has a load source group on which it can be implemented
        bmpsdf = jeeves.bmp.efficiency_bmps()
        bmpsdf = bmpsdf[~bmpsdf['bmpshortname'].isin(excluded_bmps_list())]  # remove excluded bmps
        bmpsdf = bmpsdf[bmpsdf['bmpid'].isin(TblBmpLoadSourceGroup.bmpid.tolist())]

        # Bmp names and ids are converted into python lists.
        bmp_list = bmpsdf.bmpshortname.tolist()
        self.bmpsetlist = bmp_list.copy()
        self.bmpsetidlist = bmpsdf['bmpid'].tolist()
        self.BMPS = bmp_list
        if self.save2file:
            pd.DataFrame(self.bmpsetlist, columns=['BMPS']).to_csv(os.path.join(self.instdatadir, 'data_BMPS.tab'),
                                                                   sep=' ', index=False)

        # BMP group names (and group ids) are retrieved for Bmps in the set.
        bmpgrpsdf = TblBmpGroup.loc[:, ['bmpgroupid', 'bmpgroupname']].merge(bmpsdf[['bmpgroupid', 'bmpshortname']])
        bmpgrpsetlist = list([int(x) for x in set(bmpgrpsdf.bmpgroupid)])
        self.BMPGRPS = bmpgrpsetlist
        if self.save2file:
            pd.DataFrame(bmpgrpsetlist, columns=['BMPGRPS']).to_csv(os.path.join(self.instdatadir, 'data_BMPGRPS.tab'),
                                                                    sep=' ', index=False)

        # Get correspondences between bmp names and group names (and group ids)
        # first, as dataframe column
        bmpgrpsdf['BMPGRPING'] = list(zip(bmpgrpsdf.bmpshortname, bmpgrpsdf.bmpgroupid))
        # then, also as a {grp: bmps} dictionary
        grouped = bmpgrpsdf.groupby(['bmpgroupid'])
        bmpgrping_dict = grouped['bmpshortname'].apply(lambda x: list(x)).to_dict()
        self.BMPGRPING = bmpgrping_dict
        if self.save2file:
            BMPGRPING_df_asseparatecolumns = bmpgrpsdf.loc[:, ['bmpshortname', 'bmpgroupid']].rename(
                columns={'bmpshortname': 'BMPS',
                         'bmpgroupid': 'BMPGRPS'})
            BMPGRPING_df_asseparatecolumns.to_csv(os.path.join(self.instdatadir, 'data_BMPGRPING.tab'),
                                                  sep=' ', index=False, header=['BMPS', 'BMPGRPS'])

    def _load_set_LoadSources(self, TblLandUsePreBmp, singlelsgrpdf, baseconditionid):
        """ Load Sources """
        # Limit the available set of load sources to only those:
        #  - that have base loading rates defined in the No Action data,
        #  - that have an acreage defined in TblLandUsePreBmp
        #  - "loadsource groups" that represent only a single load source
        landusedf = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid'] == baseconditionid) &
                                     (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()
        landusedf = singlelsgrpdf[singlelsgrpdf['loadsourceid'].isin(landusedf['loadsourceid'])]
        loadsrc_list = landusedf['loadsourceshortname'].tolist()

        # The load sources list is retrieved.
        self.loadsrcsetidlist = landusedf['loadsourceid'].tolist()
        self.LOADSRCS = loadsrc_list.copy()
        if self.save2file:
            pd.DataFrame(loadsrc_list, columns=['LOADSRCS']).to_csv(os.path.join(self.instdatadir, 'data_LOADSRCS.tab'),
                                                                    sep=' ', index=False)

    def _load_set_Agencies(self, TblLandUsePreBmp, TblAgency, baseconditionid):
        """ Agencies """
        landusedf = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid'] == baseconditionid) &
                                     (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()

        # Agency codes are added to the table.
        landusedf = TblAgency.loc[:, ['agencyid', 'agencycode']].merge(landusedf, how='inner')

        # The agencies list is retrieved.
        agencies_set = set(landusedf['agencycode'].tolist())
        self.AGENCIES = agencies_set
        if self.save2file:
            pd.DataFrame(agencies_set, columns=['AGENCIES']).to_csv(os.path.join(self.instdatadir, 'data_AGENCIES.tab'),
                                                                    sep=' ', index=False)

    def _load_set_Parcels(self, TblLandUsePreBmp, TblLandRiverSegment, TblLoadSource,
                          TblAgency, baseconditionid):
        """ Parcels

        These are made up of land-river segment, load source, agency index combinations that are present
        in the specified geography

        """
        df_parcels = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid'] == baseconditionid) &
                                     (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()
        df_parcels.drop(columns=['baseconditionid'], inplace=True)

        # Land river segment names, loadsource names, and agency codes are added to the table.
        df_parcels = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df_parcels, how='inner')
        df_parcels = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df_parcels, how='inner')
        df_parcels = TblAgency.loc[:, ['agencyid', 'agencycode']].merge(df_parcels, how='inner')

        # Groupby groups are converted to a dictionary ( with tuple->value structure ).
        self.PARCELS = list(zip(df_parcels['landriversegment'],
                                df_parcels['loadsourceshortname'],
                                df_parcels['agencycode']))
        if self.save2file:
            df_parcels.loc[:, ['landriversegment',
                               'loadsourceshortname',
                               'agencycode']].to_csv(os.path.join(self.instdatadir, 'data_PARCELS.tab'),
                                                     sep=' ', index=False,
                                                     header=['LRSEGS', 'LOADSRCS', 'AGENCIES'])
        return df_parcels


    def _load_set_BmpLoadSourceAssociations(self, TblBmp, TblBmpEfficiency, TblBmpGroup,
                                            TblBmpLoadSourceGroup, TblLoadSource, singlelsgrpdf):
        """ Correspondence between BMPs and LoadSources """
        # Get correspondences between BMPS, BMPGRPS, LOADSRCS, and LOADSRCGRPS, and
        #   - restrict membership to those bmps and loadsources within the sets: BMPS and LOADSRCS
        #   - add bmpgroup ids to table
        srcbmpsubtbl = TblBmpLoadSourceGroup.loc[:, :].merge(singlelsgrpdf, on='loadsourcegroupid')
        srcbmpsubtbl = srcbmpsubtbl[srcbmpsubtbl['bmpid'].isin(self.bmpsetidlist)]
        srcbmpsubtbl = srcbmpsubtbl[srcbmpsubtbl['loadsourceid'].isin(self.loadsrcsetidlist)]
        srcbmpsubtbl = TblBmp.loc[:, ['bmpid', 'bmpgroupid']].merge(srcbmpsubtbl)

        # Membership is restricted to land river segments in self.LRSEGS, so we can filter srcbmpsubtbl by effsubtable
        effsubtable = TblBmpEfficiency[TblBmpEfficiency['lrsegid'].isin(self.lrsegsetidlist)]

        # (bmp, loadsource) pairs are included in BMPSRCLINKS only if the bmp has an efficiency value
        # for that loadsource (and its associated loadsourcegroup) in TblBmpEfficiency
        bmpsrclinkssubtbl = srcbmpsubtbl.loc[:, :].merge(effsubtable.loc[:, ['bmpid', 'loadsourceid']],
                                                         on=['bmpid', 'loadsourceid'])

        # BMP, bmpgroup, and loadsource names are added to the table.
        bmpsrclinkssubtbl = TblBmp.loc[:, ['bmpid', 'bmpshortname']].merge(bmpsrclinkssubtbl)
        bmpsrclinkssubtbl = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(bmpsrclinkssubtbl)
        bmpsrclinkssubtbl = TblBmpGroup.loc[:, ['bmpgroupid', 'bmpgroupname']].merge(bmpsrclinkssubtbl)
        if self.save2file:
            bmpsrclinkssubtbl.to_csv(os.path.join(self.instdatadir, 'tempBMPSRCLINKS.csv'))

        # Duplicate pairs are removed.
        bmpsrclinkssubtbl.drop_duplicates(['bmpshortname', 'loadsourceshortname'], inplace=True)
        # Get correspondences between bmp names and loadsource names
        # first, as dataframe column
        bmpsrclinkssubtbl['BMPSRCLINKS'] = list(zip(bmpsrclinkssubtbl.bmpshortname.tolist(),
                                                    bmpsrclinkssubtbl.loadsourceshortname.tolist()))
        # then, also as a {loadsource: bmps} dictionary
        grouped = bmpsrclinkssubtbl.groupby(['loadsourceshortname'])
        self.BMPSRCLINKS = grouped['bmpshortname'].apply(lambda x: list(x)).to_dict()
        if self.save2file:
            bmpsrclinkssubtbl.loc[:, ['bmpshortname',
                                      'loadsourceshortname']].to_csv(os.path.join(self.instdatadir, 'data_BMPSRCLINKS.tab'),
                                                                     sep=' ', index=False,
                                                                     header=['BMPS', 'LOADSRCS'])

        # retain only bmp groups for the BMPGRPSRCLINKS set, and remove duplicate group pairs
        bmpsrcgrplinkssubtbl = bmpsrclinkssubtbl.loc[:, ['bmpgroupid', 'bmpgroupname',
                                                         'loadsourceshortname']].drop_duplicates(['bmpgroupname',
                                                                                                  'loadsourceshortname']).copy()
        if self.save2file:
            bmpsrcgrplinkssubtbl.to_csv(os.path.join(self.instdatadir, 'tempBMPGRPSRCLINKS.csv'))
        # Get correspondences between bmpgrp ids and loadsource names
        # first, as dataframe column
        bmpsrcgrplinkssubtbl['BMPGRPSRCLINKS'] = list(zip(bmpsrcgrplinkssubtbl.bmpgroupid.tolist(),
                                                          bmpsrcgrplinkssubtbl.loadsourceshortname.tolist()))
        # then, also as a {loadsource: bmps} dictionary
        grouped = bmpsrcgrplinkssubtbl.groupby(['loadsourceshortname'])
        bmpgrpsrclinks_dict = grouped['bmpgroupid'].apply(lambda x: list(x)).to_dict()
        self.BMPGRPSRCLINKS = bmpgrpsrclinks_dict
        if self.save2file:
            bmpsrcgrplinkssubtbl.loc[:, ['bmpgroupid',
                                         'loadsourceshortname']].to_csv(os.path.join(self.instdatadir, 'data_BMPGRPSRCLINKS.tab'),
                                                                        sep=' ', index=False,
                                                                        header=['BMPGRPS', 'LOADSRCS'])

    def _load_param_CostPerAcreOfBmps(self, TblBmp, TblCostBmpLand, costprofileid):
        """ (tau) Cost per acre ($ ac^-1) of BMP b (for cost profile κ)
        """
        # Data for 'total annualized cost per acre' is retrieved,
        # ... and only those costs pertaining to bmps in our set are retained.
        costsdf = TblCostBmpLand[TblCostBmpLand['costprofileid'] == costprofileid]
        costsdf = costsdf.merge(TblBmp[['bmpshortname', 'bmpid']])
        self.costsubtbl = costsdf
        costsdf = costsdf[costsdf['bmpshortname'].isin(self.bmpsetlist)]

        # Groupby groups are converted to a dictionary ( with tuple->value structure ).
        grouped = costsdf.groupby(['bmpshortname'])
        self.tau = grouped['totalannualizedcostperunit'].apply(lambda x: list(x)[0]).to_dict()
        if True:  # self.save2file:
            costsdf.loc[:, ['bmpshortname',
                            'totalannualizedcostperunit']].to_csv(os.path.join(self.instdatadir, 'data_tau.tab'),
                                                                  sep=' ', index=False, header=['BMPS', 'tau'])

    def _load_param_EffectivenessOfBmps(self, TblBmp, TblBmpEfficiency, TblLandRiverSegment, TblLoadSource):
        """ (eta) effectiveness (unitless) of BMP b on reducing pollutant p, in land-river segment l and load source u
        """
        # Pre-processing is necessary to build the parameter dictionary
        #  - get efficiency bmps that are in the landriversegments
        effsubtable = TblBmpEfficiency[TblBmpEfficiency['lrsegid'].isin(self.lrsegsetidlist)]
        # Pollutant names are made into an index instead of separate columns.
        listofdataframes = []
        pltntdict = {'tn': 'N', 'tp': 'P', 'sed': 'S'}
        for ps in ['tn', 'tp', 'sed']:
            bmpeff = effsubtable.loc[:, ['bmpid', 'lrsegid', 'loadsourceid', ps]]
            bmpeff['pltnt'] = pltntdict[ps]
            bmpeff.rename(columns={ps: 'effvalue'}, inplace=True)
            listofdataframes.append(bmpeff)
        df = pd.concat(listofdataframes)

        # Only those effectivenesses pertaining to - loadsources in our set, and bmps in our set - are retained.
        df = df[df['loadsourceid'].isin(self.loadsrcsetidlist)]
        df = df[df['bmpid'].isin(self.bmpsetidlist)]

        # Names (of bmps, lrsegs, and loadsources) are added to the table.
        df = TblBmp.loc[:, ['bmpid', 'bmpshortname']].merge(df)
        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)

        # Groupby groups are converted to a dictionary ( with tuple->value structure ).
        grouped = df.groupby(['bmpshortname', 'landriversegment', 'loadsourceshortname', 'pltnt'])
        self.eta = grouped['effvalue'].apply(lambda x: list(x)[0]).to_dict()
        if self.save2file:
            df.loc[:, ['bmpshortname', 'landriversegment', 'loadsourceshortname', 'pltnt',
                       'effvalue']].to_csv(os.path.join(self.instdatadir, 'data_eta.tab'),
                                           sep=' ', index=False,
                                           header=['BMPS', 'LRSEGS', 'LOADSRCS', 'PLTNTS',
                                                   'eta'])

    def _load_param_PhiBaseLoadingRates(self, TblLandRiverSegment,
                                        TblGeography, TblGeographyType, TblGeographyLrSeg,
                                        TblLoadSource, Tbl2010NoActionLoads, TblAgency):
        """ (Phi) base loading rate (lb. ac-1) of pollutant p per load source per land river segment (for year y)

        Some pre-processing is necessary to build the parameter dictionary
          - Unfortunately, the NoActionLoads table is from the website so doesn't have id numbers.
            - We'll first translate the names in the table to id numbers...

        """
        # Let's make sure the columns are all lowercase
        Tbl2010NoActionLoads.columns = map(str.lower, Tbl2010NoActionLoads.columns)

        # First, let's translate our lrseg list to full names so we can subset it before translating.
        gtypeid = TblGeographyType[TblGeographyType['geographytypefullname'] ==
                                   'Land River Segment indicating if in or out of CBWS'].geographytypeid.tolist()[0]
        geolrsegsubtbl = TblGeographyLrSeg.loc[TblGeographyLrSeg['lrsegid'].isin(self.lrsegsetidlist)]
        geosubtbl = geolrsegsubtbl.merge(TblGeography, on='geographyid', how='inner')
        lrsegfullnames = geosubtbl[geosubtbl['geographytypeid'] == gtypeid].geographyfullname.tolist()

        loadssubtbl = Tbl2010NoActionLoads[Tbl2010NoActionLoads['geography'].isin(lrsegfullnames)]

        # The load source table 'geographyfullname' column is translated to geographyid.
        includecols = ['geography', 'loadsource', 'agency', 'sector',
                       '2010 no action_amount',
                       '2010 no action_nloadeot', '2010 no action_ploadeot',
                       '2010 no action_sloadeot']
        loadssubtbl = loadssubtbl.loc[:, includecols].merge(TblGeography, how='inner',
                                                            left_on='geography',
                                                            right_on='geographyfullname')
        loadssubtbl.drop(columns=['geographyname', 'geographyfullname',
                                  'geography', 'geographytypeid'], inplace=True)

        # # Drop agencies that are not to be included
        # mask = loadssubtbl[(loadssubtbl['agency'] != self.agencyfullname)].index
        # if mask.empty:
        #     logger.warning("expected agencies besides 'Non-Federal' to be dropped")
        # loadssubtbl.drop(mask, inplace=True)

        # If division by zero occurs, those values are set to zero.
        loadssubtbl['eotn'] = (loadssubtbl['2010 no action_nloadeot'] / loadssubtbl['2010 no action_amount']).fillna(0)
        loadssubtbl["eotn"].replace([np.inf, -np.inf], 0, inplace=True)
        loadssubtbl['eotp'] = (loadssubtbl['2010 no action_ploadeot'] / loadssubtbl['2010 no action_amount']).fillna(0)
        loadssubtbl["eotp"].replace([np.inf, -np.inf], 0, inplace=True)
        loadssubtbl['eots'] = (loadssubtbl['2010 no action_sloadeot'] / loadssubtbl['2010 no action_amount']).fillna(0)
        loadssubtbl["eots"].replace([np.inf, -np.inf], 0, inplace=True)
        loadssubtbl.drop(columns=['2010 no action_nloadeot', '2010 no action_ploadeot',
                                  '2010 no action_sloadeot'], inplace=True)

        # The load source table 'geographyid' column is translated to 'lrsegid' and is then removed.
        includecols = ['geographyid', 'lrsegid']
        loadssubtbl = TblGeographyLrSeg.loc[:, includecols].merge(loadssubtbl, how='inner', on='geographyid')
        loadssubtbl.drop(columns=['geographyid'], inplace=True)

        # The load source table 'loadsource' column is translated to 'loadsourceid' and is then removed.
        includecols = ['loadsourceid', 'loadsource']
        loadssubtbl = TblLoadSource.loc[:, includecols].merge(loadssubtbl, how='inner', on='loadsource')
        loadssubtbl.drop(columns=['loadsource'], inplace=True)

        # The load source table 'agency' column is translated to 'agencycode' and is then removed.
        loadssubtbl.rename(columns={"agency": "agencyfullname"}, inplace=True)
        includecols = ['agencycode', 'agencyfullname']
        loadssubtbl = TblAgency.loc[:, includecols].merge(loadssubtbl, how='inner', on='agencyfullname')
        loadssubtbl.drop(columns=['agencyfullname'], inplace=True)

        # Only loadsources that are represented by a single-ls loadsource group are retained.
        loadssubtbl = loadssubtbl[loadssubtbl['loadsourceid'].isin(self.loadsrcsetidlist)]

        # The pollutant names are made into an index instead of separate columns.
        listofdataframes = []
        pcolnames = ['eotn', 'eotp', 'eots']
        pltntdict = {pcolnames[0]: 'N',
                     pcolnames[1]: 'P',
                     pcolnames[2]: 'S'}
        for ps in [pcolnames[0], pcolnames[1], pcolnames[2]]:
            llload = loadssubtbl.loc[:, ['lrsegid', 'loadsourceid', 'agencycode', ps]]
            llload['pltnt'] = pltntdict[ps]
            llload.rename(columns={ps: 'loadratelbsperyear'}, inplace=True)
            listofdataframes.append(llload)
        df = pd.concat(listofdataframes)

        # Names of the land river segments and load sources are added to the table.
        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)

        # Groupby groups are converted to a dictionary ( with tuple->value structure ).
        grouped = df.groupby(['landriversegment', 'loadsourceshortname', 'agencycode', 'pltnt'])
        self.phi = grouped['loadratelbsperyear'].apply(lambda x: list(x)[0]).to_dict()
        if self.save2file:
            df.loc[:, ['landriversegment', 'loadsourceshortname', 'agencycode',
                       'pltnt', 'loadratelbsperyear']].to_csv(os.path.join(self.instdatadir, 'data_phi.tab'),
                                                              sep=' ', index=False,
                                                              header=['LRSEGS', 'LOADSRCS', 'AGENCIES', 'PLTNTS', 'phi'])

    def _load_param_TotalAcresAvailableForLoadSources(self, TblLandRiverSegment, TblLoadSource,
                                                      TblLandUsePreBmp, TblAgency, baseconditionid):
        """ (alpha) total acres (ac) available for load source u on land-river segment l (for year y)

        Some pre-processing is necessary to build the parameter dictionary

        """
        df = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid'] == baseconditionid) &
                              (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()
        df.drop(columns=['baseconditionid'], inplace=True)

        # Land river segment names, loadsource names, and agency codes are added to the table.
        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df, how='inner')
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df, how='inner')
        df = TblAgency.loc[:, ['agencyid', 'agencycode']].merge(df, how='inner')

        # Groupby groups are converted to a dictionary ( with tuple->value structure ).
        grouped = df.groupby(['landriversegment', 'loadsourceshortname', 'agencycode'])
        self.alpha = grouped['acres'].apply(lambda x: list(x)[0]).to_dict()
        if self.save2file:
            df.loc[:, ['landriversegment',
                       'loadsourceshortname',
                       'agencycode',
                       'acres']].to_csv(os.path.join(self.instdatadir, 'data_alpha.tab'), sep=' ', index=False,
                                        header=['LRSEGS', 'LOADSRCS', 'AGENCIES', 'alpha'])

    def _load_already_implemented_bmps_in_a_given_scenario(self, ImpBmpSubmittedLand, ImpBmpScenarioId,
                                                           TblGeography, TblGeographyType,
                                                           TblGeographyLrSeg, TblLandRiverSegment):
        """ Implemented BMPs and their acreages
        """
        # TODO: Make this method work
        # Grab the implementation amounts for the desired scenario
        impBmp_df = ImpBmpSubmittedLand[ImpBmpSubmittedLand['scenarioid'] == ImpBmpScenarioId]
        """ columns in this dataframe include:
            ['ScenarioId', 'BmpSubmittedId', 'StateUniqueIdentifier', 'AgencyCode',
             'StateAbbreviation', 'BmpShortname', 'GeographyName', 'LoadSourceGroup',
             'Amount', 'Unit', 'AgencyId', 'StateId', 'BmpId', 'GeographyId',
             'LoadSourceGroupId', 'UnitId']
        """

        # get the values for the specified geographies (go from 'GeographyName' to 'landriversegments'
        impBmp_df = impBmp_df.merge(...)




        # get the values for only the efficiency BMPs
        """ probably will need to use one of these:
            self.bmpsetlist = bmp_list.copy()
            self.bmpsetidlist = bmpsdf['bmpid'].tolist()
            self.BMPS = bmp_list
            
            # Maybe this ->> impBmp_df = impBmp_df[impBmp_df['BmpShortname'].isin(self.bmpsetlist)]
        """

        # Convert units to Acres where needed

        # put the values into a new dataframe of this form: ['LandRiverSegment', 'LoadSource', 'Agency', 'BmpShortName', 'Amount', 'Unit']




# dl = Lrseg(save2file=False, geolist=['N51059PL7_4960_0000'])
# print(dl.lrsegsetlist)
# print(dl.lrsegsetidlist)
# print(dl.LRSEGS)