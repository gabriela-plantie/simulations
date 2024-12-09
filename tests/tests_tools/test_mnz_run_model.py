from minizinc_tools.run_mnz_model import run_model
from minizinc_tools.transform_data_for_mnz_input import minizinc_input


def test_run_model():

    model_file = "tests/tests_tools/model_for_test.mnz"

    with open(model_file, "r") as file:
        model_text = file.read()

    data_text = minizinc_input(
        {
            "n": 3,
            "domain_min": 2,
            "domain_max": 4,
        }
    )

    result = run_model(model_text=[model_text, data_text], verbose=True)
    assert result.status.name == "SATISFIED"
    assert result.solution.x == [2, 3, 4]
