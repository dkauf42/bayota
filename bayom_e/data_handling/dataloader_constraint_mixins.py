
# Generic/Built-in
import os
import logging

# Computation
import pandas as pd

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
        theta indexed by [PLTNTS]
    """

    def _load_constraint(self):
        logger.debug('loading county level load constraint')
        """ (Theta) target percent load reductions (%) per pollutant p """
        Thetadict = {}
        for k in self.pltntslist:
            Thetadict[k] = 5
        self.Theta = Thetadict

        if self.save2file:
            theta_df = pd.DataFrame(list(Thetadict.items()), columns=['theta'])
            theta_df[['PLTNTS']] = theta_df.apply(pd.Series)
            theta_df.loc[:, ['PLTNTS', 'theta']].to_csv(os.path.join(self.instdatadir, 'data_theta.tab'), sep=' ', index=False)


class DataLoadConstraintAtLrsegLevelMixin(object):
    """
    Parameters:
        theta indexed by [LRSEGS, PLTNTS]
    """

    def _load_constraint(self):
        logger.debug('loading lrseg level load constraint')
        """ (Theta) target percent load reductions (%) per pollutant p and land river segment l """
        Thetadict = {}
        for l in self.lrsegsetlist:
            for k in self.pltntslist:
                Thetadict[(l, k)] = 5
            # Thetadict[(l, 'N')] = 5
            # Thetadict[(l, 'P')] = 5
            # Thetadict[(l, 'S')] = 5
        self.theta = Thetadict
        if self.save2file:
            theta_df = pd.DataFrame(list(Thetadict.items()), columns=['LRSEGS', 'theta'])
            theta_df[['LRSEGS', 'PLTNTS']] = theta_df['LRSEGS'].apply(pd.Series)
            theta_df.loc[:, ['LRSEGS', 'PLTNTS', 'theta']].to_csv(os.path.join(self.instdatadir, 'data_theta.tab'), sep=' ', index=False)
