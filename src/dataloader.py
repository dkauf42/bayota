import os
import pandas as pd
from sys import path as pylib  #im naming it as pylib so that we won't get confused between os.path and sys.path
pylib += [os.path.abspath(r'/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/'
                          r'CRC_ResearchScientist_Optimization/Optimization_Tool/'
                          r'2_ExperimentFolder/CastJeeves')]
from CastJeeves.jeeves import Jeeves

jeeves = Jeeves()


class DataLoader:
    def __init__(self, save2file=True, lrsegs_list=None):
        # Save instance data to file?
        self.save2file = save2file

        """ Instance Specifiers """
        baseconditionid = 29
        costprofileid = 4

        """ Data File Paths """
        baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
        # amplappdir = os.path.join(baseexppath, 'ampl/amplide.macosx64/')
        projectpath = os.path.join(baseexppath, 'OptEfficiencySubProblem/')
        datapath = os.path.join(baseexppath, 'OptEfficiencySubProblem/data/raw/')

        # # Specify model and data files
        # # f_mod = os.path.join(baseexppath, 'ampl/example/steel3.mod')
        # f_mod = os.path.join(projectpath, 'test7.mod')
        # # f_dat = os.path.join(baseexppath, 'ampl/example/steel3.dat')
        # f_dat = os.path.join(projectpath, 'test6.dat')

        # Data table directories
        sourcedatadir = os.path.join(baseexppath, 'OptSandbox/data/test_source/')
        metadatadir = os.path.join(baseexppath, 'OptSandbox/data/test_metadata/')

        """ Data tables for the set definitions """
        TblBmp = pd.read_csv(os.path.join(sourcedatadir, 'TblBmp.csv'))
        TblBmpGroup = pd.read_csv(os.path.join(sourcedatadir, 'TblBmpGroup.csv'))
        TblBmpLoadSourceGroup = pd.read_csv(os.path.join(sourcedatadir, 'TblBmpLoadSourceGroup.csv'))
        TblBmpType = pd.read_csv(os.path.join(sourcedatadir, 'TblBmpType.csv'))

        TblLoadSource = pd.read_csv(os.path.join(sourcedatadir, 'TblLoadSource.csv'), skipinitialspace=True)
        TblLoadSource['loadsource'] = TblLoadSource[
            'loadsource'].str.strip()  # There is an extra space after "Specialty Crop Low" that needs to be removed.

        TblLoadSourceGroup = pd.read_csv(os.path.join(sourcedatadir, 'TblLoadSourceGroup.csv'))
        TblLoadSourceGroupLoadSource = pd.read_csv(os.path.join(sourcedatadir, 'TblLoadSourceGroupLoadSource.csv'))
        TblLandRiverSegment = pd.read_csv(os.path.join(sourcedatadir, 'TblLandRiverSegment.csv'))

        TblGeography = pd.read_csv(os.path.join(sourcedatadir, 'TblGeography.csv'))
        TblGeographyLrSeg = pd.read_csv(os.path.join(sourcedatadir, 'TblGeographyLrSeg.csv'))
        TblGeographyType = pd.read_csv(os.path.join(sourcedatadir, 'TblGeographyType.csv'))

        # Data tables for the parameter definitions
        TblCostBmpLand = pd.read_csv(os.path.join(metadatadir, 'TblCostBmpLand.csv'))
        TblBmpEfficiency = pd.read_csv(os.path.join(sourcedatadir, 'TblBmpEfficiency.csv'))
        # Target load reductions ???  (set this ourselves??)
        TblLandUsePreBmp = pd.read_csv(os.path.join(sourcedatadir, 'TblLandUsePreBmp.csv'))
        Tbl2010NoActionLoads = pd.read_csv(os.path.join(datapath, '2010NoActionLoads.csv'))

        # Data table generated by separate python script, the set of load source *groups* where each load source *group* contains one and only one load source
        singlelsgrpdf = pd.read_csv(os.path.join(datapath, 'single-ls_groups.csv'))

        self.PLTNTS = pd.DataFrame()
        self.LRSEGS = pd.DataFrame()
        self.BMPS = pd.DataFrame()
        self.BMPGRPS = pd.DataFrame()
        self.BMPGRPING = pd.DataFrame()
        self.LOADSRCS = pd.DataFrame()
        self.BMPSRCLINKS = pd.DataFrame()
        self.BMPGRPSRCLINKS = pd.DataFrame()
        self.c = pd.DataFrame()
        self.E = pd.DataFrame()
        self.tau = pd.DataFrame()
        self.phi = pd.DataFrame()
        self.T = pd.DataFrame()

        # lists that will be populated by loading the Set data
        self.lrsegsetlist = []
        self.lrsegsetidlist = []
        self.bmpsetlist = []
        self.bmpsetidlist = []
        self.loadsrcsetidlist = []
        self.load_sets(self.save2file, TblLandRiverSegment, TblBmp, TblBmpType, TblBmpEfficiency,
                       TblBmpGroup, TblBmpLoadSourceGroup, TblLoadSource, TblLandUsePreBmp,
                       singlelsgrpdf, baseconditionid, lrsegs_list=lrsegs_list)

        self.costsubtbl = pd.DataFrame()
        self.load_params(self.save2file, TblBmp, TblCostBmpLand, TblBmpEfficiency, TblLandRiverSegment,
                    TblGeography, TblGeographyType, TblGeographyLrSeg,
                    TblLoadSource, TblLandUsePreBmp, Tbl2010NoActionLoads,
                    baseconditionid, costprofileid)

    def load_sets(self, save2file, TblLandRiverSegment, TblBmp, TblBmpType, TblBmpEfficiency,
                  TblBmpGroup, TblBmpLoadSourceGroup, TblLoadSource, TblLandUsePreBmp,
                  singlelsgrpdf, baseconditionid,
                  lrsegs_list=None):
        """ ****************** Sets Data ****************** """

        """ Pollutants """
        p_list = ['N', 'P', 'S']
        self.PLTNTS = p_list
        if save2file:
            df = pd.DataFrame(p_list, columns=['PLTNTS']).to_csv('data_PLTNTS.tab', sep=' ', index=False)

        """ Land River Segments """
        # lrsegs_list = ['N51133RL0_6450_0000']
        # lrsegs_list = ['N42071SL2_2410_2700']
        lrsegs_list = lrsegs_list
        if not lrsegs_list:
            lrsegs_list = ['N42071SL2_2410_2700']
        lrsegids = TblLandRiverSegment[TblLandRiverSegment['landriversegment'] == lrsegs_list[0]].lrsegid.tolist()
        self.lrsegsetlist = list([x for x in lrsegs_list])
        self.lrsegsetidlist = lrsegids
        self.LRSEGS = lrsegs_list
        if save2file:
            pd.DataFrame(lrsegs_list, columns=['LRSEGS']).to_csv('data_LRSEGS.tab', sep=' ', index=False)

        """ BMPs """
        self.load_set_BMPs(save2file, TblBmp, TblBmpType, TblBmpLoadSourceGroup, TblBmpGroup)

        """ Load Sources """
        self.load_set_LoadSources(save2file, TblLandUsePreBmp, singlelsgrpdf, baseconditionid)

        """ Correspondence between BMPs and LoadSources """
        # Get correspondences between BMPS, BMPGRPS, LOADSRCS, and LOADSRCGRPS, and
        #   - restrict membership to those bmps and loadsources within the sets: BMPS and LOADSRCS
        #   - add bmpgroup ids to table
        srcbmpsubtbl = TblBmpLoadSourceGroup.loc[:, :].merge(singlelsgrpdf, on='loadsourcegroupid')
        srcbmpsubtbl = srcbmpsubtbl[srcbmpsubtbl['bmpid'].isin(self.bmpsetidlist)]
        srcbmpsubtbl = srcbmpsubtbl[srcbmpsubtbl['loadsourceid'].isin(self.loadsrcsetidlist)]
        srcbmpsubtbl = TblBmp.loc[:, ['bmpid', 'bmpgroupid']].merge(srcbmpsubtbl)

        # Restrict membership to the land river segments in LRSEGS, so we can filter srcbmpsubtbl by effsubtable
        effsubtable = TblBmpEfficiency[TblBmpEfficiency['lrsegid'].isin(self.lrsegsetidlist)]

        # Include (b, lambda) pairs in BMPSRCLINKS only if the b has an efficiency value
        # for that lambda (and its associated loadsourcegroup) in TblBmpEfficiency
        # retain only the (b, lambda) pairs in the srcbmpsubtbl with effectiveness values
        bmpsrclinkssubtbl = srcbmpsubtbl.loc[:, :].merge(effsubtable.loc[:, ['bmpid', 'loadsourceid']],
                                                         on=['bmpid', 'loadsourceid'])

        # Add BMP, bmpgroup, and loadsource names to table
        bmpsrclinkssubtbl = TblBmp.loc[:, ['bmpid', 'bmpshortname']].merge(bmpsrclinkssubtbl)
        bmpsrclinkssubtbl = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(bmpsrclinkssubtbl)
        bmpsrclinkssubtbl = TblBmpGroup.loc[:, ['bmpgroupid', 'bmpgroupname']].merge(bmpsrclinkssubtbl)
        if save2file:
            bmpsrclinkssubtbl.to_csv('tempBMPSRCLINKS.csv')

        # retain only bmp groups for the BMPGRPSRCLINKS set
        bmpsrcgrplinkssubtbl = bmpsrclinkssubtbl.drop_duplicates(['bmpgroupname', 'loadsourceshortname']).copy()
        if save2file:
            bmpsrcgrplinkssubtbl.to_csv('tempBMPGRPSRCLINKS.csv')
        bmpsrclinkssubtbl['BMPSRCLINKS'] = list(zip(bmpsrclinkssubtbl.bmpshortname.tolist(),
                                                    bmpsrclinkssubtbl.loadsourceshortname.tolist()))
        self.BMPSRCLINKS = list(bmpsrclinkssubtbl.BMPSRCLINKS)
        if save2file:
            bmpsrclinkssubtbl.loc[:, ['bmpshortname',
                                      'loadsourceshortname']].to_csv('data_BMPSRCLINKS.tab',
                                                                     sep=' ', index=False,
                                                                     header=['BMPS', 'LOADSRCS'])

        bmpsrcgrplinkssubtbl['BMPGRPSRCLINKS'] = list(zip(bmpsrcgrplinkssubtbl.bmpgroupid.tolist(),
                                                          bmpsrcgrplinkssubtbl.loadsourceshortname.tolist()))
        self.BMPGRPSRCLINKS = list(bmpsrcgrplinkssubtbl.BMPGRPSRCLINKS)
        if save2file:
            bmpsrcgrplinkssubtbl.loc[:, ['bmpgroupid',
                                         'loadsourceshortname']].to_csv('data_BMPGRPSRCLINKS.tab',
                                                                        sep=' ', index=False,
                                                                        header=['BMPGRPS', 'LOADSRCS'])

    def load_set_BMPs(self, save2file, TblBmp, TblBmpType, TblBmpLoadSourceGroup, TblBmpGroup):
        """ BMPs """
        # Get efficiency type id, and then restrict BMPs by:
        #  - Only include b if it's an 'efficiency' BMP
        #  - Only include b if it has a load source group on which it can be implemented
        # efftypeid = TblBmpType[TblBmpType['bmptype'] == 'Efficiency']['bmptypeid'].tolist()[0]
        # bmpsdf = TblBmp[TblBmp['bmptypeid'] == efftypeid]

        # Get efficiency bmps, and then restrict by:
        #  - Only include b if it has a load source group on which it can be implemented
        bmpsdf = jeeves.bmp.efficiency_bmps()
        bmpsdf = bmpsdf[bmpsdf['bmpid'].isin(TblBmpLoadSourceGroup.bmpid.tolist())]

        # Convert bmp names and ids into python lists
        self.bmpsetlist = list([x for x in bmpsdf.bmpshortname.tolist()])
        self.bmpsetidlist = bmpsdf.bmpid.tolist()
        self.BMPS = list(self.bmpsetlist)
        if save2file:
            pd.DataFrame(self.bmpsetlist, columns=['BMPS']).to_csv('data_BMPS.tab', sep=' ', index=False)

        # Get BMP group names (and group ids) for bmps in the set
        bmpgrpsdf = TblBmpGroup.loc[:, ['bmpgroupid', 'bmpgroupname']].merge(bmpsdf[['bmpgroupid', 'bmpshortname']])
        bmpgrpsetlist = list([int(x) for x in set(bmpgrpsdf.bmpgroupid)])
        self.BMPGRPS = bmpgrpsetlist
        if save2file:
            pd.DataFrame(bmpgrpsetlist, columns=['BMPGRPS']).to_csv('data_BMPGRPS.tab', sep=' ', index=False)

        # Get correspondences between bmp names and group names (and group ids)
        bmpgrpsdf['BMPGRPING'] = list(zip(bmpgrpsdf.bmpshortname, bmpgrpsdf.bmpgroupid))
        self.BMPGRPING = list(bmpgrpsdf.BMPGRPING)
        if save2file:
            BMPGRPING_df_asseparatecolumns = bmpgrpsdf.loc[:, ['bmpshortname', 'bmpgroupid']].rename(
                columns={'bmpshortname': 'BMPS',
                         'bmpgroupid': 'BMPGRPS'})
            BMPGRPING_df_asseparatecolumns.to_csv('data_BMPGRPING.tab', sep=' ', index=False,
                                                  header=['BMPS', 'BMPGRPS'])

    def load_set_LoadSources(self, save2file, TblLandUsePreBmp, singlelsgrpdf, baseconditionid):
        """ Load Sources """
        # Limit the available set of load sources to only those:
        #  - that have base loading rates defined in the No Action data,
        #  - that have an acreage defined in TblLandUsePreBmp
        #  - "loadsource groups" that represent only a single load source
        landusedf = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid'] == baseconditionid) &
                                     (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()
        landusedf = singlelsgrpdf[singlelsgrpdf['loadsourceid'].isin(landusedf['loadsourceid'])]

        # Get load sources list
        loadsrcsetlist = list([x for x in landusedf.loadsourceshortname.tolist()])
        self.loadsrcsetidlist = landusedf.loadsourceid.tolist()
        self.LOADSRCS = loadsrcsetlist
        if save2file:
            pd.DataFrame(loadsrcsetlist, columns=['LOADSRCS']).to_csv('data_LOADSRCS.tab', sep=' ', index=False)

    def load_params(self, save2file, TblBmp, TblCostBmpLand, TblBmpEfficiency, TblLandRiverSegment,
                    TblGeography, TblGeographyType, TblGeographyLrSeg,
                    TblLoadSource, TblLandUsePreBmp, Tbl2010NoActionLoads,
                    baseconditionid, costprofileid):
        """ ****************** Parameter Data ****************** """

        """ (c) Cost per acre ($ ac^-1) of BMP b (for cost profile κ) """
        # Get total annualized cost per unit data, and retain only:
        #  - those costs pertaining to bmps in our set
        costsdf = TblCostBmpLand[TblCostBmpLand['costprofileid'] == costprofileid]
        costsdf = costsdf.merge(TblBmp[['bmpshortname', 'bmpid']])
        self.costsubtbl = costsdf
        costsdf = costsdf[costsdf['bmpshortname'].isin(self.bmpsetlist)]

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = costsdf.groupby(['bmpshortname'])
        self.c = grouped['totalannualizedcostperunit'].apply(lambda x: list(x)[0]).to_dict()
        if save2file:
            costsdf.loc[:, ['bmpshortname',
                            'totalannualizedcostperunit']].to_csv('data_c.tab', sep=' ',
                                                                  index=False, header=['BMPS', 'c'])

        """ (E) effectiveness (unitless) of BMP b on reducing pollutant p, in land-river segment l and load source λ """
        # Pre-processing is necessary to build the parameter dictionary
        #  - get efficiency bmps that are in the landriversegments
        effsubtable = TblBmpEfficiency[TblBmpEfficiency['lrsegid'].isin(self.lrsegsetidlist)]
        # make the pollutant names into an index instead of separate columns
        listofdataframes = []
        pltntdict = {'tn': 'N', 'tp': 'P', 'sed': 'S'}
        for ps in ['tn', 'tp', 'sed']:
            bmpeff = effsubtable.loc[:, ['bmpid', 'lrsegid', 'loadsourceid', ps]]
            bmpeff['pltnt'] = pltntdict[ps]
            bmpeff.rename(columns={ps: 'effvalue'}, inplace=True)
            listofdataframes.append(bmpeff)
        df = pd.concat(listofdataframes)

        # Retain only those effectivenesses pertaining to:
        #  - loadsources in our set, and bmps in our set
        df = df[df['loadsourceid'].isin(self.loadsrcsetidlist)]
        df = df[df['bmpid'].isin(self.bmpsetidlist)]

        # Add names (of bmps, lrsegs, and loadsources) to the table
        df = TblBmp.loc[:, ['bmpid', 'bmpshortname']].merge(df)
        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)
        #display(df[df['bmpid'] == 48])

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = df.groupby(['bmpshortname', 'pltnt', 'landriversegment', 'loadsourceshortname'])
        self.E = grouped['effvalue'].apply(lambda x: list(x)[0]).to_dict()
        if save2file:
            df.loc[:, ['bmpshortname', 'pltnt', 'landriversegment',
                       'loadsourceshortname', 'effvalue']].to_csv('data_E.tab', sep=' ', index=False,
                                                                  header=['BMPS', 'PLTNTS', 'LRSEGS', 'LOADSRCS', 'E'])

        """ (Tau) target percent load reductions (%) per pollutant p and land river segment l """
        Taudict = {}
        for l in self.lrsegsetlist:
            Taudict[(l, 'N')] = 5
            Taudict[(l, 'P')] = 5
            Taudict[(l, 'S')] = 5
        self.tau = Taudict
        if save2file:
            tau_df = pd.DataFrame(list(Taudict.items()), columns=['LRSEGS', 'tau'])
            tau_df[['LRSEGS', 'PLTNTS']] = tau_df['LRSEGS'].apply(pd.Series)
            tau_df.loc[:, ['LRSEGS', 'PLTNTS', 'tau']].to_csv('data_tau.tab', sep=' ', index=False)

        """ (Phi) base loading rate (lb. ac-1) of pollutant p per load source per land river segment (for year y) """
        # Some pre-processing is necessary to build the parameter dictionary
        #   - Unfortunately, the NoActionLoads table is from the website so doesn't have id numbers.
        #     - Let's translate this table to id numbers...
        # Let's make sure the columns are all lowercase
        Tbl2010NoActionLoads.columns = map(str.lower, Tbl2010NoActionLoads.columns)

        # First, let's translate our lrseg list to full names so we can subset it before translating.
        gtypeid = TblGeographyType[TblGeographyType['geographytypefullname'] == 'Land River Segment indicating if in or out of CBWS'].geographytypeid.tolist()[0]
        geolrsegsubtbl = TblGeographyLrSeg.loc[TblGeographyLrSeg['lrsegid'].isin(self.lrsegsetidlist)]
        geosubtbl = geolrsegsubtbl.merge(TblGeography, on='geographyid', how='inner')
        lrsegfullnames = geosubtbl[geosubtbl['geographytypeid'] == gtypeid].geographyfullname.tolist()

        loadssubtbl = Tbl2010NoActionLoads[Tbl2010NoActionLoads['geography'].isin(lrsegfullnames)]

        # Go from load source table with geographyfullname to geographyid
        includecols = ['geography', 'loadsource', '2010 no action_nloadeot', '2010 no action_ploadeot', '2010 no action_sloadeot']
        loadssubtbl = loadssubtbl.loc[:, includecols].merge(TblGeography, how='inner',
                                                            left_on='geography',
                                                            right_on='geographyfullname')
        loadssubtbl.drop(columns=['geographyname', 'geographyfullname',
                                  'geography', 'geographytypeid'], inplace=True)

        # Go from load source table with geographyid to lrsegid
        includecols = ['geographyid', 'lrsegid']
        loadssubtbl = TblGeographyLrSeg.loc[:, includecols].merge(loadssubtbl, how='inner',
                                                                  on='geographyid')
        loadssubtbl.drop(columns=['geographyid'], inplace=True)

        # Go from LoadSource to loadsourceid
        includecols = ['loadsourceid', 'loadsource']
        loadssubtbl = TblLoadSource.loc[:, includecols].merge(loadssubtbl, how='inner',
                                                              on='loadsource')
        loadssubtbl.drop(columns=['loadsource'], inplace=True)

        # only retain loadsources that are represented by a single-ls loadsource group.
        loadssubtbl = loadssubtbl[loadssubtbl['loadsourceid'].isin(self.loadsrcsetidlist)]

        # make the pollutant names into an index instead of separate columns
        listofdataframes = []
        pcolnames = ['2010 no action_nloadeot', '2010 no action_ploadeot', '2010 no action_sloadeot']
        pltntdict = {pcolnames[0]: 'N',
                     pcolnames[1]: 'P',
                     pcolnames[2]: 'S'}
        for ps in [pcolnames[0], pcolnames[1], pcolnames[2]]:
            llload = loadssubtbl.loc[:, ['lrsegid', 'loadsourceid', ps]]
            llload['pltnt'] = pltntdict[ps]
            llload.rename(columns={ps: 'loadratelbsperyear'}, inplace=True)
            listofdataframes.append(llload)
        df = pd.concat(listofdataframes)

        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = df.groupby(['landriversegment', 'loadsourceshortname', 'pltnt'])
        self.phi = grouped['loadratelbsperyear'].apply(lambda x: list(x)[0]).to_dict()
        if save2file:
            df.loc[:, ['landriversegment', 'loadsourceshortname',
                       'pltnt', 'loadratelbsperyear']].to_csv('data_phi.tab', sep=' ', index=False,
                                                              header=['LRSEGS', 'LOADSRCS', 'PLTNTS', 'phi'])

        """ (T) total acres (ac) available for load source λ on land-river segment l (for year y) """
        # Some pre-processing is necessary to build the parameter dictionary
        df = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid'] == baseconditionid) &
                              (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()

        df.drop(columns=['baseconditionid'], inplace=True)
        df.drop(columns=['agencyid'], inplace=True)  # and drop agency (for now!)

        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = df.groupby(['landriversegment', 'loadsourceshortname'])
        self.T = grouped['acres'].apply(lambda x: list(x)[0]).to_dict()
        if save2file:
            df.loc[:, ['landriversegment',
                       'loadsourceshortname',
                       'acres']].to_csv('data_T.tab', sep=' ', index=False,
                                        header=['LRSEGS', 'LOADSRCS', 'T'])
