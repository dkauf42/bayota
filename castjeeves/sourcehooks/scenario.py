from .sourcehooks import SourceHook


class Scenario(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Methods for querying CAST data related to Scenarios """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

    def get_baseconditionid(self,
                            landchangemodelscenario='',
                            baseyear=''):
        """

        Args:
            landchangemodelscenario (str): typically either 'Historic Trends' or 'Current Zoning'
            baseyear (int or str): e.g. 2010 or '2010'

        Returns:
            baseconditionid (int)

        """
        if isinstance(baseyear, int):
            pass
        elif isinstance(baseyear, str):
            baseyear = int(baseyear)
        else:
            raise ValueError("baseyear must be 'int' or 'str'")

        TblLCMS = self.source.TblLandChangeModelScenario  # get relevant source data
        TblBC = self.source.TblBaseCondition  # get relevant source data

        row = TblLCMS.loc[TblLCMS['landchangemodelscenarioname'] == landchangemodelscenario]
        lcmsid = row['landchangemodelscenarioid'].item()

        row = TblBC.loc[(TblBC['landchangemodelscenarioid'] == lcmsid) &
                        (TblBC['baseyear'] == baseyear)]
        bcid = row['baseconditionid'].item()

        return bcid
