import importlib
from ..TableLoader import TableLoader

tblList = ["ImpBmpSubmittedAnimal",
           "ImpBmpSubmittedCropAppRateReduction",
           "ImpBmpSubmittedLand",
           "ImpBmpSubmittedManureTransport",
           "ImpBmpSubmittedRelatedMeasure",
           "InvalidBmpSubmittedAnimal",
           "InvalidBmpSubmittedCropAppRateReduction",
           "InvalidBmpSubmittedLand",
           "InvalidBmpSubmittedManureTransport",
           "TblPointSourceDataSets",
           "TblScenario",
           "TblScenarioGeography"
           ]


class Metadata(TableLoader):
    def __init__(self, dfDict = None):
        super().__init__(tblList)
        if isinstance(dfDict, dict):
            for key in dfDict:
                self.addTable(dfDict[key])
                
    @classmethod
    def loadDataBaseTables(cls, scenarioId):
        obj = cls()
        for tbl in obj.getTblList():
            loc = ".sqlserver." + tbl
            module = importlib.import_module(loc, __package__)
            # filter tables on specified scenarioId
            df = module.df
            if "scenarioid" in df.columns.tolist():
                df = df.ix[df.scenarioid == scenarioId].reset_index()
            obj.addTable(tbl, df)
        return obj
