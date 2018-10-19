import pandas as pd

import logging
logger = logging.getLogger(__name__)


class DataCostConstraintMixin(object):
    """
    Parameters:
        totalcostupperbound indexed by []
    """

    def _load_constraint(self):
        logger.debug('loading total cost constraint')
        """ Total Cost constraint for entire  """
        self.totalcostupperbound = 100000  # a default
        if self.save2file:
            totalcostupperbound_df = pd.DataFrame(list(self.totalcostupperbound), columns=['totalcostupperbound'])
            totalcostupperbound_df.to_csv('data_totalcostupperbound.tab', sep=' ', index=False)


class DataLoadConstraintAtCountyLevelMixin(object):
    """
    Parameters:
        tau indexed by [PLTNTS]
    """

    def _load_constraint(self):
        logger.debug('loading county level load constraint')
        """ (Tau) target percent load reductions (%) per pollutant p """
        Taudict = {'N': 5,
                   'P': 5,
                   'S': 5}
        self.tau = Taudict
        if self.save2file:
            tau_df = pd.DataFrame(list(Taudict.items()), columns=['tau'])
            tau_df[['PLTNTS']] = tau_df.apply(pd.Series)
            tau_df.loc[:, ['PLTNTS', 'tau']].to_csv('data_tau.tab', sep=' ', index=False)


class DataLoadConstraintAtLrsegLevelMixin(object):
    """
    Parameters:
        tau indexed by [LRSEGS, PLTNTS]
    """

    def _load_constraint(self):
        logger.debug('loading lrseg level load constraint')
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
