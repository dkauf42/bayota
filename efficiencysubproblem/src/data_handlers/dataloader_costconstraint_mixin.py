import pandas as pd


class CostConstraintMixin(object):
    def _load_constraint(self):
        print('CostConstraintMixin._load_constraint()')
        """ Total Cost constraint for entire  """
        self.totalcostupperbound = 100000  # a default
        if self.save2file:
            totalcostupperbound_df = pd.DataFrame(list(self.totalcostupperbound), columns=['totalcostupperbound'])
            totalcostupperbound_df.to_csv('data_totalcostupperbound.tab', sep=' ', index=False)
