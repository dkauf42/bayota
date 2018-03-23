import importlib
from ..TableLoader import TableLoader

tblList = ["TblAgency",
           "TblAnimal",
           "TblAnimalGroup",
           "TblAnimalGroupAnimal",
           "TblAnimalPastureFraction",
           # "TblAnimalPastureStockingRate",
           "TblAnimalPopulation",
           "TblAnimalYearly",
           "TblBiosolids",
           "TblBmp",
           "TblBmpAnimalEfficiency",
           "TblBmpBackout",
           "TblBmpGroup",
           "TblBmpLoadSourceFromTo",
           "TblBmpManureIncorporationEfficiency",
           # "TblBmpTypeGroup",
           # "TblBmpTypeGroupLoadSourceFromTo",
           "TblBmpUnit",
           "TblBmpUplandAcresFactor",
           "TblCounty",
           "TblCrop",
           "TblCropApplicationRate",
           "TblCropCoverFraction",
           "TblCropLoadSourceFractions",
           "TblCropDetachedStorage",
           "TblCropPlantHarvestDate",
           "TblCropUptakeAndRemoval",
           "TblCropYield",
           # "TblCsoAreaInLrsegforNpdes",
           # "TblCsoConnections",
           "TblCsoPassThruFactors",
           "TblCsoNpdes",
           "TblDays",
           "TblGeography",
           "TblGeographyLrSeg",
           "TblLandCover",
           # "TblLandCoverAgFractionsPostTrueUp",
           "TblLandRiverSegment",
           "TblLandUsePreBmp",
           "TblLoadSourceGroup",
           "TblLoadSourceGroupLoadSource",
           "TblLoadsStreamShore",
           "TblLoadSource",
           "TblNutrient",
           "TblNutrientConcentration",
           "TblNutrientSpreadBiosolidCurve",
           "TblNutrientSpreadManureCurve",
           "TblNutrientVolatilization",
           "TblSepticSystems",
           "TblState",
           "TblUnit",
           "vwGeographyCounty",
           "vwCropHeatUnitsMonthly",
           "vwCropHeatUnitsYearly",
           "vwCropApplicationFractionsMonthly",
           "TblFertilizerLbsInWatershed",
           "TblFertilizerNutrientFractions",
           # "TblFertilizer",
           "TblNutrientSpreadFertNCurve",
           "TblNutrientSpreadFertPCurve",
           # "TblFertilizerFractionAppliedWithLastSales",
           "TblFertilizerAdjustmentFromLastManureTransport",
           "TblSepticPassThroughFactors",
           "TblBmpEfficiency",
           "TblSepticRibData",
           "TblSepticRibSystemType",
           "TblCropDoubleCrop",
           "TblAnimalFractionInLrseg",
           "TblBaseCondition",
           "TblCropNeedFractionMetHistorically",
           "TblClimateChangeData",
           "TblCropCFactor",
           "TblCalibrationInputAverages",
           "TblSoilPData",
           "TblLoadsBAL",
           "TblLoadSensitivitiesToInputs",
           "TblAtmDepData",
           "TblCalibrationAverageCFactor",
           "TblSoilPCalcData",
           "TblSoilPAdjFactor",
           "TblLoadFactorsLandToWater",
           "TblAnimalFeedSpaceSedimentRate",
           "TblGeographyLrseg",
           "TblBmpConversionFactor",
           "TblCsoTenYearAvgLoads",
           "TblPointSourceNpdes",
           "TblPointSourceData",
           "TblLoadsCALMinusSTB",
           "TblLoadFactorsStreamToRiver",
           "TblLoadFactorsRiverToBay",
           "TblBmpEmissionReductions",
           "TblBmpEmissionManureTreatmentTech",
           "TblLandRiverSegmentAgencyLoadSource"
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
            module = importlib.import_module(loc, __package__)
            obj.addTable(tbl, module.df)
        return obj
