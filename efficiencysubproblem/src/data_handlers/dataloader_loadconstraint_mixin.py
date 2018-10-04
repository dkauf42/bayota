import pandas as pd


class LoadConstraintMixin(object):
    def _load_constraint(self):
        print('LoadConstraintMixin._load_constraint()')
        """ (Tau) target percent load reductions (%) per pollutant p and land river segment l """
        Taudict = {}
        for l in self.lrsegsetlist:
            Taudict[(l, 'N')] = 5
            Taudict[(l, 'P')] = 5
            Taudict[(l, 'S')] = 5
        self.tau = Taudict
        if self.save2file:
            tau_df = pd.DataFrame(list(Taudict.items()), columns=['LRSEGS', 'tau'])
            tau_df[['LRSEGS', 'PLTNTS']] = tau_df['LRSEGS'].apply(pd.Series)
            tau_df.loc[:, ['LRSEGS', 'PLTNTS', 'tau']].to_csv('data_tau.tab', sep=' ', index=False)