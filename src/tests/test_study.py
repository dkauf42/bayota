from src.study import Study


def test_default_study_instantiation():
    study = Study()
    assert study.numberofrunscompleted == 0