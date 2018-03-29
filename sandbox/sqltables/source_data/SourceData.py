import importlib
from ..TableLoader import TableLoader

tblList = ["TblAgency",
           "TblAnimal",
           "TblAnimalGroup",
           "TblAnimalGroupAnimal",
           # "TblAnimalPastureFraction",
           # "TblAnimalPastureStockingRate",
           "TblAnimalPopulation",
           # "TblAnimalYearly",
           # "TblBiosolids",
           "TblBmp",
           # "TblBmpAnimalEfficiency",
           "TblBmpAnimalGroup",
           # "TblBmpBackout",
           "TblBmpGroup",
           "TblBmpLoadSourceFromTo",
           "TblBmpLoadSourceGroup",
           # "TblBmpManureIncorporationEfficiency",
           "TblBmpScenarioType",
           "TblBmpSector",
           "TblBmpType",
           # "TblBmpTypeGroup",
           # "TblBmpTypeGroupLoadSourceFromTo",
           "TblBmpUnit",
           # "TblBmpUplandAcresFactor",
           "TblCostBmpUnit",
           "TblCounty",
           "TblCrop",
           # "TblCropApplicationRate",
           # "TblCropCoverFraction",
           # "TblCropDetachedStorage",
           # "TblCropDoubleCrop",
           "TblCropLoadSource",
           "TblCropLoadSourceFractions",
           # "TblCropPlantHarvestDate",
           # "TblCropUptakeAndRemoval",
           # "TblCropYield",
           # "TblCsoAreaInLrsegforNpdes",
           # "TblCsoConnections",
           # "TblCsoNpdes",
           # "TblCsoPassThruFactors",
           # "TblDays",
           "TblGeography",
           "TblGeographyLrSeg",
           "TblGeographyNpdes",
           "TblGeographyType",
           # "TblHydroGeoMorphicRegion",
           "TblLandCover",
           # "TblLandCoverAgFractionsPostTrueUp",
           "TblLandCoverPermittedAcres",
           "TblLandRiverSegment",
           "TblLandRiverSegmentAgency",
           "TblLandRiverSegmentAgencyLoadSource",
           "TblLandUsePreBmp",
           "TblLoadSourceGroup",
           "TblLoadSourceGroupLoadSource",
           "TblLoadsStreamShore",
           "TblLoadSource",
           # "TblLoadSourceAggregate",
           # "TblLoadSourceAggregateLoadSource",
           # "TblLoadSourceAggregateType",
           # "TblLoadSourceAllocationType",
           "TblLoadSourceGroup",
           "TblLoadSourceGroupLoadSource",
           "TblLoadSourceGroupSector",
           "TblLoadSourceMajor",
           "TblLoadSourceMinor",
           "TblLoadType",
           # "TblNutrient",
           # "TblNutrientConcentration",
           # "TblNutrientSpreadBiosolidCurve",
           # "TblNutrientSpreadManureCurve",
           # "TblNutrientVolatilization",
           # "TblPointSourceData",
           # "TblPointSourceNpdes",
           "TblSector",
           "TblSepticSystems",
           "TblState",
           "TblUnit",
           "TblUnitRelation",
           "TblUnitType",
           # "vwCropHeatUnitsMonthly",
           # "vwCropHeatUnitsYearly",
           # "vwCropApplicationFractionsMonthly",
           # "TblFertilizerLbsInWatershed",
           # "TblFertilizerNutrientFractions",
           # "TblFertilizer",
           "vwGeographyCounty",
           "vwGeographyNameState",
           "vwGeographyNpdesPointSourceData",
           "vwLandEfficiencyBMPspt1",
           "vwLandRiverSegmentDetails",
           "vwLandRiverSegmentGeography",
           ]


class SourceData(TableLoader):
    def __init__(self, dfDict=None):
        super().__init__(tblList)
        if isinstance(dfDict, dict):
            for key in dfDict:
                self.addTable(dfDict[key])
    
    @classmethod
    def loadDataBaseTables(cls):
        obj = cls()
        for tbl in obj.getTblList():
            loc = ".sqlserver." + tbl
            print(loc)
            module = importlib.import_module(loc, __package__)
            obj.addTable(tbl, module.df)
        return obj

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        print("SourceData.__get_state__(): I'm being pickled")
        odict = self.__dict__.copy()    # get attribute dictionary
        # print('I need to save this list:', self.getTblList())
        # odict['tempTableSetForPickling'] = self.getTblList()
        return odict

    def __setstate__(self, odict):
        print("SourceData.__set_state__(): I'm being unpickled with these values:", odict)
        self.__dict__ = odict     # make dict our attribute dictionary
