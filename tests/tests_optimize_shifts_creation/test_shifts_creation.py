import pytest

from minizinc_tools.run_mnz_model import run_model
from minizinc_tools.transform_data_for_mnz_input import minizinc_input
from optimize_shift_creation.create_shifts_ortools_cp import CPShifts
from optimize_shift_creation.utils import format_output


@pytest.mark.parametrize(
    "min_len, max_len, estimated_rider_demand,"
    "expected_objective_value, num_expected_shifts_by_init_and_len",
    [
        (1, 2, [2], 0, {(0, 1): 2}),
        # this could return also {(0,2): 2} # make a logic to choose only one option
        # (1, 2, [2, 2], {(0, 1): 2, (1, 1): 2}),
        (3, 3, [8, 8, 8], 0, {(0, 3): 8}),
        # # 9 shifts of len 3 and startime 0 -> obj = 2
        (3, 3, [10, 9, 8], 2, {(0, 3): 9}),
        (2, 3, [1, 2, 2], 0, {(0, 3): 1, (1, 2): 1}),
        # (2, 3, [2, 2, 1], 0, {(0, 2): 1, (0, 3): 1}),  # failing test
    ],
)
def test_rider_demand_satisfaction(
    min_len,
    max_len,
    estimated_rider_demand,
    expected_objective_value,
    num_expected_shifts_by_init_and_len,
):

    estimated_rider_demand = {t: d for t, d in enumerate(estimated_rider_demand)}
    cp_shift = CPShifts(estimated_rider_demand)
    objective, shifts = cp_shift.create_shifts(min_len=min_len, max_len=max_len)

    assert (
        objective == expected_objective_value
    ), f"objective value is {objective} and should be {expected_objective_value}"
    assert {
        s: v for s, v in shifts.items() if s[1] > 0
    } == num_expected_shifts_by_init_and_len


model_file = "optimize_shift_creation/create_shifts_mnz.mzn"


@pytest.mark.parametrize(
    "min_len, max_len, estimated_rider_demand,"
    "expected_objective_value, num_expected_shifts_by_init_and_len",
    [
        (1, 2, [2], 0, {(0, 1): 2}),
        # this could return also {(0,2): 2} # make a logic to choose only one option
        # (1, 2, [2, 2], {(0, 1): 2, (1, 1): 2}),
        (3, 3, [8, 8, 8], 0, {(0, 3): 8}),
        # # 9 shifts of len 3 and startime 0 -> obj = 2
        (3, 3, [10, 9, 8], 2, {(0, 3): 9}),
        (2, 3, [1, 2, 2], 0, {(0, 3): 1, (1, 2): 1}),
        # (2, 3, [2, 2, 1], 0, {(0, 2): 1, (0, 3): 1}),  # failing test
    ],
)
def test_staffing_cp_mnz(
    min_len,
    max_len,
    estimated_rider_demand,
    expected_objective_value,
    num_expected_shifts_by_init_and_len,
):
    with open(model_file, "r") as file:
        model_text = file.read()

    # estimated_rider_demand = [1,2,3]
    # min_len = 3
    # max_len= 3
    # expected_objective_value = 0
    input_dict = {
        "min_len": min_len,
        "max_len": max_len,
        "rider_demand": estimated_rider_demand,
        "times": len(estimated_rider_demand),
    }

    data_text = minizinc_input(input_dict)
    result = run_model(model_text=[model_text, data_text], verbose=True)
    assert result.objective == expected_objective_value
    assert (
        format_output(
            [t - 1 for t in result.solution.starts_at], result.solution.length
        )
        == num_expected_shifts_by_init_and_len
    )
