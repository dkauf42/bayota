import pytest
from efficiencysubproblem.src.study import Study


def test_default_study_instantiation():
    with pytest.raises(ValueError):
        Study()

def test_study_lrseg_instantiation():
    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=5, saveData2file=False)
    assert study.numberofrunscompleted == 0

def test_study_county_instantiation():
    study = Study(objectivetype='costmin',
                  geoscale='county', geoentities=['Northumberland, VA'],
                  baseconstraint=5, saveData2file=False)
    assert study.numberofrunscompleted == 0