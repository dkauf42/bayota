

class QryBase:
    def __init__(self, tables=None):
        """Wrapper for Base Condition data table. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """
        self.tables = tables

    def get_agencies_in_lrsegs(self, lrsegs=None):
        """Determine the agencies that have nonzero acreage in the specified lrsegs

        Queries the BaseCondition table with a pd.Series that can be used as boolean mask

        Args:
            lrsegs (pandas.Series): series of lrseg string specifiers
        """
        lsacres = self.tables.basecond.LSacres

        boolseries = lsacres['LandRiverSegment'].isin(lrsegs)
        lsacres = lsacres.loc[boolseries, :].copy()

        grouped = lsacres.groupby(['LandRiverSegment', 'AgencyCode'])

        summed = grouped.sum()
        summed = summed.iloc[summed.PreBMPAcres.nonzero()[0]]

        return list(summed.index.get_level_values('AgencyCode').unique().values)
