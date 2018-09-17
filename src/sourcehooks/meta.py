from .sourcehooks import SourceHook


class Metadata(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Metadata Methods """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

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
        TblCostProfile = self.meta.TblCostProfile  # get relevant source data
        return TblCostProfile.loc[:, 'costprofilename']

    def get_baseconditionid(self, baseyear=None, baseconditionname=None):
        TblBaseCondition = self.source.TblBaseCondition  # get relevant source data
        TblLandChangeModelScenario = self.source.TblLandChangeModelScenario

        row = TblLandChangeModelScenario[(TblLandChangeModelScenario.landchangemodelscenarioname == baseconditionname)]
        if row.empty:
            raise ValueError('Base Condition (year or name) not found!')
        if type(baseyear) == str:
            baseyear = int(baseyear)
        row = TblBaseCondition[(TblBaseCondition.baseyear == baseyear) &
                               (TblBaseCondition.landchangemodelscenarioid == row['landchangemodelscenarioid'][0])]
        return row[['baseconditionid']]
