import os
import pandas as pd


class DataLoader:
    def __init__(self, save2file=True):
        # Save instance data to file?
        self.save2file = save2file

        """ Instance Specifiers """
        baseconditionid = 29
        costprofileid = 4

        """ Data File Paths """
        baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
        # amplappdir = os.path.join(baseexppath, 'ampl/amplide.macosx64/')
        projectpath = os.path.join(baseexppath, 'ampl/OptEfficiencySubProblem/')
        datapath = os.path.join(baseexppath, 'ampl/OptEfficiencySubProblem/data/')

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
                       singlelsgrpdf, baseconditionid)

        self.costsubtbl = pd.DataFrame()
        self.load_params(self.save2file, TblBmp, TblCostBmpLand, TblBmpEfficiency, TblLandRiverSegment,
                    TblGeography, TblGeographyType, TblGeographyLrSeg,
                    TblLoadSource, TblLandUsePreBmp, Tbl2010NoActionLoads,
                    baseconditionid, costprofileid)

    def load_sets(self, save2file, TblLandRiverSegment, TblBmp, TblBmpType, TblBmpEfficiency,
                  TblBmpGroup, TblBmpLoadSourceGroup, TblLoadSource, TblLandUsePreBmp,
                  singlelsgrpdf, baseconditionid):
        """ ****************** Sets Data ****************** """

        """ Pollutants and Landriversegments """
        p_list = ['N', 'P', 'S']
        df = pd.DataFrame(p_list, columns=['PLTNTS'])
        PLTNTS_df = df.loc[:, ['PLTNTS']]
        self.PLTNTS = list(PLTNTS_df.PLTNTS)
        if save2file:
            PLTNTS_df.to_csv('data_PLTNTS.tab', sep=' ', index=False)

        # lrsegs_list = ['N51133RL0_6450_0000']
        lrsegs_list = ['N42071SL2_2410_2700']
        lrsegids = TblLandRiverSegment[TblLandRiverSegment['landriversegment'] == lrsegs_list[0]].lrsegid.tolist()
        self.lrsegsetlist = list([x for x in lrsegs_list])
        self.lrsegsetidlist = lrsegids

        df = pd.DataFrame(lrsegs_list, columns=['LRSEGS'])
        LRSEGS_df = df.loc[:, ['LRSEGS']]
        self.LRSEGS = list(LRSEGS_df.LRSEGS)
        if save2file:
            LRSEGS_df.to_csv('data_LRSEGS.tab', sep=' ', index=False)

        """ BMPs """
        # Restrict BMPs to include:
        #  - Only include b if it's an 'efficiency' BMP
        #  - Only include b if it has a load source group on which it can be implemented
        efftypeid = TblBmpType[TblBmpType['bmptype'] == 'Efficiency']['bmptypeid'].tolist()[0]
        bmpsdf = TblBmp[TblBmp['bmptypeid'] == (efftypeid)]
        bmpsdf = bmpsdf[bmpsdf['bmpid'].isin(TblBmpLoadSourceGroup.bmpid.tolist())]

        self.bmpsetlist = list([x for x in bmpsdf.bmpshortname.tolist()])
        self.bmpsetidlist = bmpsdf.bmpid.tolist()
        #display(self.bmpsetlist[:5])
        df = pd.DataFrame(self.bmpsetlist, columns=['BMPS'])
        BMPS_df = df.loc[:, ['BMPS']]
        self.BMPS = list(BMPS_df.BMPS)
        if save2file:
            BMPS_df.to_csv('data_BMPS.tab', sep=' ', index=False)

        bmpgrpsdf = TblBmpGroup.loc[:, ['bmpgroupid', 'bmpgroupname']].merge(bmpsdf[['bmpgroupid', 'bmpshortname']])
        bmpgrpsetlist = list([int(x) for x in set(bmpgrpsdf.bmpgroupid)])
        #display(bmpgrpsetlist[:5])
        df = pd.DataFrame(bmpgrpsetlist, columns=['BMPGRPS'])
        BMPGRPS_df = df.loc[:, ['BMPGRPS']]
        self.BMPGRPS = list(BMPGRPS_df.BMPGRPS)
        if save2file:
            BMPGRPS_df.to_csv('data_BMPGRPS.tab', sep=' ', index=False)

        bmpgrpingsetlist = list(zip(bmpgrpsdf.bmpshortname.tolist(),
                                    bmpgrpsdf.bmpgroupid.tolist()))
        #display(bmpgrpingsetlist)
        bmpgrpsdf['BMPGRPING'] = list(zip(bmpgrpsdf.bmpshortname, bmpgrpsdf.bmpgroupid))
        BMPGRPING_df_asseparatecolumns = bmpgrpsdf.loc[:, ['bmpshortname', 'bmpgroupid']].rename(columns={'bmpshortname': 'BMPS',
                                                                                        'bmpgroupid': 'BMPGRPS'})
        self.BMPGRPING = list(bmpgrpsdf.BMPGRPING)
        if save2file:
            BMPGRPING_df_asseparatecolumns.to_csv('data_BMPGRPING.tab', sep=' ', index=False,
                                                  header=['BMPS', 'BMPGRPS'])

        """ Load Sources """
        # limit the load sources set to only include those that have
        #  base loading rates defined in the No Action data,
        #  and only those that have an acreage defined in TblLandUsePreBmp
        landusedf = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid']==baseconditionid) &
                                     (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()
        landusedf = singlelsgrpdf[singlelsgrpdf['loadsourceid'].isin(landusedf['loadsourceid'])]
        #display(landusedf.head(1))

        loadsrcsetlist = list([x for x in landusedf.loadsourceshortname.tolist()])
        self.loadsrcsetidlist = landusedf.loadsourceid.tolist()
        df = pd.DataFrame(loadsrcsetlist, columns=['LOADSRCS'])
        LOADSRCS_df = df.loc[:, ['LOADSRCS']]
        self.LOADSRCS = list(LOADSRCS_df.LOADSRCS)
        if save2file:
            LOADSRCS_df.to_csv('data_LOADSRCS.tab', sep=' ', index=False)

        # --- Get the correspondences between BMPS, BMPGRPS, LOADSRCS, and LOADSRCGRPS ---
        srcbmpsubtbl = TblBmpLoadSourceGroup.loc[:, :].merge(singlelsgrpdf, on='loadsourcegroupid')
        # restrict membership to those bmps and loadsources within the sets BMPS and LOADSRCS
        srcbmpsubtbl = srcbmpsubtbl[srcbmpsubtbl['bmpid'].isin(self.bmpsetidlist)]
        srcbmpsubtbl = srcbmpsubtbl[srcbmpsubtbl['loadsourceid'].isin(self.loadsrcsetidlist)]
        # Add bmpgroup ids
        srcbmpsubtbl = TblBmp.loc[:, ['bmpid', 'bmpgroupid']].merge(srcbmpsubtbl)

        # --- Only include (b, lambda) pairs in BMPSRCLINKS if its b has an efficiency value ---
        # --- for that lambda (and its associated loadsourcegroup) in TblBmpEfficiency ---
        # restrict membership to the land river segments in LRSEGS
        effsubtable = TblBmpEfficiency[TblBmpEfficiency['lrsegid'].isin(self.lrsegsetidlist)]

        # retain only the (b, lambda) pairs in the srcbmpsubtbl with effec tiveness values
        bmpsrclinkssubtbl = srcbmpsubtbl.loc[:, :].merge(effsubtable.loc[:, ['bmpid', 'loadsourceid']],
                                                         on=['bmpid', 'loadsourceid'])
        #display('after filtering srcbmpsubtbl by effsubtable')
        #display(bmpsrclinkssubtbl.head(2))

        # Add BMP, bmpgroup, and loadsource names
        bmpsrclinkssubtbl = TblBmp.loc[:, ['bmpid', 'bmpshortname']].merge(bmpsrclinkssubtbl)
        bmpsrclinkssubtbl = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(bmpsrclinkssubtbl)
        bmpsrclinkssubtbl = TblBmpGroup.loc[:, ['bmpgroupid', 'bmpgroupname']].merge(bmpsrclinkssubtbl)
        if save2file:
            bmpsrclinkssubtbl.to_csv('tempBMPSRCLINKS.csv')
        #display('after adding names to table')
        #display(bmpsrclinkssubtbl.head(2))

        # retain only bmp groups for the BMPGRPSRCLINKS set
        bmpsrcgrplinkssubtbl = bmpsrclinkssubtbl.drop_duplicates(['bmpgroupname', 'loadsourceshortname']).copy()
        if save2file:
            bmpsrcgrplinkssubtbl.to_csv('tempBMPGRPSRCLINKS.csv')
        #display('after retaining only bmp groups')
        #display(bmpsrcgrplinkssubtbl.head(2))
        bmpsrclinkssubtbl['BMPSRCLINKS'] = list(zip(bmpsrclinkssubtbl.bmpshortname.tolist(),
                                                    bmpsrclinkssubtbl.loadsourceshortname.tolist()))
        self.BMPSRCLINKS = list(bmpsrclinkssubtbl.BMPSRCLINKS)
        BMPSRCLINKS_df_asseparatecolumns = bmpsrclinkssubtbl.loc[:, ['bmpshortname', 'loadsourceshortname']]
        if save2file:
            BMPSRCLINKS_df_asseparatecolumns.to_csv('data_BMPSRCLINKS.tab', sep=' ', index=False,
                                                    header=['BMPS', 'LOADSRCS'])

        bmpsrcgrplinkssubtbl['BMPGRPSRCLINKS'] = list(zip(bmpsrcgrplinkssubtbl.bmpgroupid.tolist(),
                                                          bmpsrcgrplinkssubtbl.loadsourceshortname.tolist()))
        self.BMPGRPSRCLINKS = list(bmpsrcgrplinkssubtbl.BMPGRPSRCLINKS)
        #display(self.BMPGRPSRCLINKS)
        BMPGRPSRCLINKS_df_asseparatecolumns = bmpsrcgrplinkssubtbl.loc[:, ['bmpgroupid', 'loadsourceshortname']]
        if save2file:
            BMPGRPSRCLINKS_df_asseparatecolumns.to_csv('data_BMPGRPSRCLINKS.tab', sep=' ', index=False,
                                                       header=['BMPGRPS', 'LOADSRCS'])

    def load_params(self, save2file, TblBmp, TblCostBmpLand, TblBmpEfficiency, TblLandRiverSegment,
                    TblGeography, TblGeographyType, TblGeographyLrSeg,
                    TblLoadSource, TblLandUsePreBmp, Tbl2010NoActionLoads,
                    baseconditionid, costprofileid):
        """ Costs per Unit of BMP """
        costsdf = TblCostBmpLand[TblCostBmpLand['costprofileid'] == costprofileid]
        # Retain only those costs pertaining to bmps in our set
        costsdf = costsdf.merge(TblBmp[['bmpshortname', 'bmpid']])
        self.costsubtbl = costsdf
        costsdf = costsdf[costsdf['bmpshortname'].isin(self.bmpsetlist)]
        #display(costsdf.head(5))

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = costsdf.groupby(['bmpshortname'])
        cdict = grouped['totalannualizedcostperunit'].apply(lambda x: list(x)[0]).to_dict()
        #display(cdict)
        self.c = cdict

        # costsdf['c'] = list(zip(costsdf.bmpshortname.tolist(),
        #                         costsdf.totalannualizedcostperunit.tolist()))
        # self.c = list(costsdf.c)
        c_df_asseparatecolumns = costsdf.loc[:, ['bmpshortname', 'totalannualizedcostperunit']]
        if save2file:
            c_df_asseparatecolumns.to_csv('data_c.tab', sep=' ', index=False, header=['BMPS', 'c'])

        """ Efficiency Values """
        # Some pre-processing is necessary to build the parameter dictionary
        #display(self.bmpsetidlist[:5])
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

        # Retain only those effectivenesses pertaining to loadsources in our set
        df = df[df['loadsourceid'].isin(self.loadsrcsetidlist)]
        # Retain only those costs pertaining to bmps in our set
        df = df[df['bmpid'].isin(self.bmpsetidlist)]
        #display(df.head(5))

        df = TblBmp.loc[:, ['bmpid', 'bmpshortname']].merge(df)
        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)
        #display(df.head(5))
        #display(df[df['bmpid'] == 48])

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = df.groupby(['bmpshortname', 'pltnt', 'landriversegment', 'loadsourceshortname'])
        Edict = grouped['effvalue'].apply(lambda x: list(x)[0]).to_dict()
        #display(Edict)
        self.E = Edict

        E_df_asseparatecolumns = df.loc[:, ['bmpshortname', 'pltnt', 'landriversegment',
                                            'loadsourceshortname', 'effvalue']]
        if save2file:
            E_df_asseparatecolumns.to_csv('data_E.tab', sep=' ', index=False,
                          header=['BMPS', 'PLTNTS', 'LRSEGS', 'LOADSRCS', 'E'])

        """ Tau, """
        Taudict = {}
        for l in self.lrsegsetlist:
            Taudict[(l, 'N')] = 5
            Taudict[(l, 'P')] = 5
            Taudict[(l, 'S')] = 5

        tau_df = pd.DataFrame(list(Taudict.items()), columns=['LRSEGS', 'tau'])
        tau_df[['LRSEGS', 'PLTNTS']] = tau_df['LRSEGS'].apply(pd.Series)
        #display(tau_df)
        self.tau = Taudict
        tau_df_asseparatecolumns = tau_df.loc[:, ['LRSEGS', 'PLTNTS', 'tau']]
        if save2file:
            tau_df_asseparatecolumns.to_csv('data_tau.tab', sep=' ', index=False)

        """ Phi """
        # Some pre-processing is necessary to build the parameter dictionary
        # Unfortunately, the NoActionLoads table is from the website so doesn't have id numbers.  Let's translate this table to id numbers...
        # Let's make sure the columns are all lowercase
        Tbl2010NoActionLoads.columns = map(str.lower, Tbl2010NoActionLoads.columns)

        # First, let's translate our lrseg list to the fullnames so we can subset it before translating.
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
        #display(loadssubtbl.head(2))

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
        #display(df.head(5))

        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)
        #display(df.head(5))

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = df.groupby(['landriversegment', 'loadsourceshortname', 'pltnt'])
        Phidict = grouped['loadratelbsperyear'].apply(lambda x: list(x)[0]).to_dict()
        #display(Phidict)
        self.phi = Phidict

        phi_df_asseparatecolumns = df.loc[:, ['landriversegment', 'loadsourceshortname',
                                              'pltnt', 'loadratelbsperyear']]
        if save2file:
            phi_df_asseparatecolumns.to_csv('data_phi.tab', sep=' ', index=False,
                                            header=['LRSEGS', 'LOADSRCS', 'PLTNTS', 'phi'])

        """ T """
        # Some pre-processing is necessary to build the parameter dictionary
        df = TblLandUsePreBmp[(TblLandUsePreBmp['baseconditionid'] == baseconditionid) &
                              (TblLandUsePreBmp['lrsegid'].isin(self.lrsegsetidlist))].copy()

        df.drop(columns=['baseconditionid'], inplace=True)
        # and drop agency (for now!)
        df.drop(columns=['agencyid'], inplace=True)
        #display(df.head(2))

        df = TblLandRiverSegment.loc[:, ['lrsegid', 'landriversegment']].merge(df)
        df = TblLoadSource.loc[:, ['loadsourceid', 'loadsourceshortname']].merge(df)
        #display(df.head(2))

        # Convert groups to dictionary ( with tuple->value structure )
        grouped = df.groupby(['landriversegment', 'loadsourceshortname'])
        Tdict = grouped['acres'].apply(lambda x: list(x)[0]).to_dict()
        #display(Tdict)
        self.T = Tdict
        T_df_asseparatecolumns = df.loc[:, ['landriversegment', 'loadsourceshortname', 'acres']]
        if save2file:
            T_df_asseparatecolumns.to_csv('data_T.tab', sep=' ', index=False,
                                          header=['LRSEGS', 'LOADSRCS', 'T'])
