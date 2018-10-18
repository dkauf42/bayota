import pytest
from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solver_handling.solvehandler import SolveHandler


@pytest.fixture(scope='module')
def valid_ipopt_available_on_env_path(request):
    return SolveHandler(solvername='ipopt').get_solver_path()


def test_study_instantiation_noargs():
    with pytest.raises(ValueError):
        Study()


def test_study_instantiation_badobjective():
    with pytest.raises(ValueError):
        Study(objectivetype='Dennis Nedry')


def test_study_instantiation_scale_entities_mismatch():
    with pytest.raises(ValueError):
        s = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['Montgomery, MD'],
                  baseconstraint=1)


def test_study_lrseg_costmin_instantiation():
    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=5, saveData2file=False)
    assert study.numberofrunscompleted == 0


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


def test_study_bad_mix_of_WVcounty_and_NYstate():
    with pytest.raises(ValueError):
        s = Study(objectivetype='costmin',
                  geoscale='county', geoentities=['Hardy, NY'],
                  baseconstraint=5)


def test_study_bad_mix_of_lrseg_scale_and_county_entities():
    with pytest.raises(ValueError):
        s = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['Hardy, WV'],
                  baseconstraint=5)


def test_study_solutionobjectivevalue_costmin_lrsegNorthumberlandCountyVA(valid_ipopt_available_on_env_path):
    if not valid_ipopt_available_on_env_path:
        pytest.skip("unsupported configuration - ipopt not available on env path")

    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  baseconstraint=5, saveData2file=False)

    solver_output_filepaths, solution_csv_filepath, mdf, solution_objective = study.go()

    assert 20675 == round(solution_objective)


def test_study_solutionobjectivevalue_costmin_lrsegMontgomeryCountyMD(valid_ipopt_available_on_env_path):
    if not valid_ipopt_available_on_env_path:
        pytest.skip("unsupported configuration - ipopt not available on env path")

    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N24031PM0_4640_4820'],  # Cabin John Creek, in Montgomery County
                  baseconstraint=5, saveData2file=False)

    solver_output_filepaths, solution_csv_filepath, mdf, solution_objective = study.go()

    assert 8 == round(solution_objective)


def test_study_solutionobjectivevalue_costmin_countyMontgomeryCountyMD(valid_ipopt_available_on_env_path):
    if not valid_ipopt_available_on_env_path:
        pytest.skip("unsupported configuration - ipopt not available on env path")

    study = Study(objectivetype='costmin',
                  geoscale='county', geoentities=['Montgomery, MD'],
                  baseconstraint=5)

    solver_output_filepaths, solution_csv_filepath, mdf, solution_objective = study.go()

    assert 5637 == round(solution_objective)
