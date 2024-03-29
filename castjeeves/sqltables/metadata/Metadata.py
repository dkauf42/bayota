import importlib
from ..TableLoader import TableLoader

tblList = [# "ImpBmpSubmittedAnimal",
           # "ImpBmpSubmittedCropAppRateReduction",
           "ImpBmpSubmittedLand",
           # "ImpBmpSubmittedManureTransport",
           # "ImpBmpSubmittedRelatedMeasure",
           # "InvalidBmpSubmittedAnimal",
           # "InvalidBmpSubmittedCropAppRateReduction",
           "InvalidBmpSubmittedLand",
           # "InvalidBmpSubmittedManureTransport",
           "TblCostBmpAnimal",
           "TblCostBmpLand",
           "TblCostProfile",
           # "TblPointSourceDataSets",
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

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        print("MetaData.__get_state__(): I'm being pickled")
        odict = self.__dict__.copy()    # get attribute dictionary
        # print('I need to save this list:', self.getTblList())
        # odict['tempTableSetForPickling'] = self.getTblList()
        return odict

    def __setstate__(self, odict):
        print("MetaData.__set_state__(): I'm being unpickled with these values:", odict)
        self.__dict__ = odict     # make dict our attribute dictionary
