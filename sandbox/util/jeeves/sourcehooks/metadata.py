from sandbox.util.jeeves.sourcehooks.sourcehooks import SourceHook


class Metadata(SourceHook):
    def __init__(self, sourcedata=None):
        """ Metadata Methods """
        SourceHook.__init__(self, sourcedata=sourcedata)

    # Methods to get metadata options
    def all_base_year_names(self):
        TblBaseYear = self.source.TblBaseYear  # get relevant source data
        return TblBaseYear.loc[:, 'baseyear']

    def all_base_condition_names(self):
        TblLandChangeModelScenario = self.source.TblLandChangeModelScenario  # get relevant source data
        return TblLandChangeModelScenario.loc[:, 'landchangemodelscenarioname']

    def wastewaterdata_names(self):
        return ['WasteWater0001', 'WasteWater0002', 'WasteWater0003', 'WasteWater0004']

    def costprofile_names(self):
        return ['CostProfile0001', 'CostProfile0002', 'CostProfile0003', 'CostProfile0004']
