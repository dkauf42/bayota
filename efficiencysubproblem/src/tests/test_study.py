import pytest
from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solver_handling.solvehandler import SolveHandler


@pytest.fixture(scope='module')
def valid_ipopt_available_on_env_path(request):
    return SolveHandler(solvername='ipopt').get_solver_path()


def test_study_instantiation_noargs():
    with pytest.raises(TypeError):
        Study()


def test_study_instantiation_badobjective():
    with pytest.raises(ValueError):
        Study(objectivetype='Dennis Nedry',
              geoscale='lrseg', geoentities=['Montgomery, MD'])


def test_study_instantiation_scale_entities_mismatch():
    with pytest.raises(ValueError):
        s = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['Montgomery, MD'])


def test_study_lrseg_costmin_instantiation():
    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  saveData2file=False)
    assert study.numberofrunscompleted == 0


def test_study_county_costmin_instantiation():
    study = Study(objectivetype='costmin',
                  geoscale='county', geoentities=['Northumberland, VA'],
                  saveData2file=False)
    assert study.numberofrunscompleted == 0


def test_study_lrseg_loadreductionmax_instantiation():
    study = Study(objectivetype='loadreductionmax',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  saveData2file=False)
    assert study.numberofrunscompleted == 0


def test_study_county_loadreductionmax_instantiation():
    study = Study(objectivetype='loadreductionmax',
                  geoscale='county', geoentities=['Northumberland, VA'],
                  saveData2file=False)
    assert study.numberofrunscompleted == 0


def test_study_bad_mix_of_WVcounty_and_NYstate():
    with pytest.raises(ValueError):
        s = Study(objectivetype='costmin',
                  geoscale='county', geoentities=['Hardy, NY'])


def test_study_bad_mix_of_lrseg_scale_and_county_entities():
    with pytest.raises(ValueError):
        s = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['Hardy, WV'])


def test_study_solutionobjectivevalue_costmin_lrsegNorthumberlandCountyVA(valid_ipopt_available_on_env_path):
    if not valid_ipopt_available_on_env_path:
        pytest.skip("unsupported configuration - ipopt not available on env path")

    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N51133RL0_6450_0000'],  # lrseg in Northumberland County, VA
                  saveData2file=False)

    (solver_output_filepath,
     solution_csv_filepath,
     sorteddf_byacres,
     solution_objective,
     feasible_solution) = study.go(constraint=5, fileprintlevel=0)

    assert 20675 == round(solution_objective)


def test_study_solutionobjectivevalue_costmin_lrsegMontgomeryCountyMD(valid_ipopt_available_on_env_path):
    if not valid_ipopt_available_on_env_path:
        pytest.skip("unsupported configuration - ipopt not available on env path")

    study = Study(objectivetype='costmin',
                  geoscale='lrseg', geoentities=['N24031PM0_4640_4820'],  # Cabin John Creek, in Montgomery County
                  saveData2file=False)

    (solver_output_filepath,
     solution_csv_filepath,
     sorteddf_byacres,
     solution_objective,
     feasible_solution) = study.go(constraint=5, fileprintlevel=0)

    assert 8 == round(solution_objective)


def test_study_solutionobjectivevalue_costmin_countyMontgomeryCountyMD(valid_ipopt_available_on_env_path):
    if not valid_ipopt_available_on_env_path:
        pytest.skip("unsupported configuration - ipopt not available on env path")

    study = Study(objectivetype='costmin',
                  geoscale='county', geoentities=['Montgomery, MD'])

    (solver_output_filepath,
     solution_csv_filepath,
     sorteddf_byacres,
     solution_objective,
     feasible_solution) = study.go(constraint=5, fileprintlevel=0)

    assert 5637 == round(solution_objective)
