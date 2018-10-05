import pytest
from efficiencysubproblem.src.study import Study


def test_study_instantiation_noargs():
    with pytest.raises(ValueError):
        Study()


def test_study_instantiation_badobjective():
    with pytest.raises(ValueError):
        Study(objectivetype='Dennis Nedry')


def test_study_lrseg_costmin_instantiation():
    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=5, saveData2file=False)
    assert study.numberofrunscompleted == 0


def test_study_lrseg_costmin_solutionobjectivevalue():
    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=5, saveData2file=False)

    solver_output_filepaths, solution_csv_filepath, mdf, solution_objective = study.go()

    assert 20675 == round(solution_objective)


def test_study_lrseg_costmin_instantiation_multirun_check():
    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=[3, 5], saveData2file=False)
    assert study.multirun == True


def test_study_county_costmin_instantiation():
    study = Study(objectivetype='costmin',
                  geoscale='county', geoentities=['Northumberland, VA'],
                  baseconstraint=5, saveData2file=False)
    assert study.numberofrunscompleted == 0


def test_study_lrseg_loadreductionmax_instantiation():
    study = Study(objectivetype='loadreductionmax',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=100000, saveData2file=False)
    assert study.numberofrunscompleted == 0


def test_study_lrseg_loadreductionmax_instantiation_multirun_check():
    study = Study(objectivetype='loadreductionmax',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=[100000, 200000], saveData2file=False)
    assert study.multirun is True


def test_study_county_loadreductionmax_instantiation():
    study = Study(objectivetype='loadreductionmax',
                  geoscale='county', geoentities=['Northumberland, VA'],
                  baseconstraint=100000, saveData2file=False)
    assert study.numberofrunscompleted == 0
