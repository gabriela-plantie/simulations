import numpy as np
import pytest

from optimize_shift_creation.minizinc.create_shifts_mzn_cp import CPShiftsMzn
from optimize_shift_creation.ortools.create_shifts_ortools_cp import CPShifts


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


path = "optimize_shift_creation/minizinc"
model_file = f"{path}/create_shifts_mnz_1.mzn"

# improves model 1 usign channeling constraints
model_file = f"{path}/create_shifts_mnz_3.mzn"

# different point of view
model_file = f"{path}/create_shifts_mnz_2.mzn"


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
        (2, 3, [2, 2, 1], 0, {(0, 2): 1, (0, 3): 1}),
        # (2, 3, [2, 2, 1, 2, 2], 0, {(0, 3): 1, (0, 2): 1, (3, 2): 2}),
        (1, 2, [2, 2], 0, {(0, 2): 2}),  # prioritize longer shifts
        (1, 10, [3] * 10, 0, {(0, 10): 3}),  # prioritize longer shifts
        # cases found by random search
        (2, 2, [9, 8, 4, 2], 3, {(0, 2): 8, (2, 2): 3}),  # fixed
        (2, 2, [2, 3, 0, 9], 1 + 25 + 16, {(0, 2): 2, (2, 2): 4}),  # failing
    ],
)
def test_staffing_cp_mnz_logic(
    min_len,
    max_len,
    estimated_rider_demand,
    expected_objective_value,
    num_expected_shifts_by_init_and_len,
):
    input_dict = {
        "min_len": min_len,
        "max_len": max_len,
        "rider_demand": estimated_rider_demand,
        "times": len(estimated_rider_demand),
    }

    model = CPShiftsMzn(input_data=input_dict)
    result = model.solve(model_file, timeout=5)

    assert result["slack_sum"] == expected_objective_value
    assert result["shifts"] == num_expected_shifts_by_init_and_len


@pytest.mark.parametrize(
    "min_len, max_len, estimated_rider_demand,"
    "expected_objective_value, num_expected_shifts_by_init_and_len",
    [
        (2, 2, [1] * 10, 0, {(0, 2): 1, (2, 2): 1, (4, 2): 1, (6, 2): 1, (8, 2): 1}),
        (1, 2, [2] * 10, 0, {(0, 2): 2, (2, 2): 2, (4, 2): 2, (6, 2): 2, (8, 2): 2}),
        (
            2,
            2,
            [10] * 10,
            0,
            {(0, 2): 10, (2, 2): 10, (4, 2): 10, (6, 2): 10, (8, 2): 10},
        ),  # test speed -> symmetry
        (
            1,
            2,
            [100] * 10,
            0,
            {(0, 2): 100, (2, 2): 100, (4, 2): 100, (6, 2): 100, (8, 2): 100},
        ),  # test speed -> dominance
        (
            1,
            5,
            [100] * 5,
            0,
            {(0, 5): 100},
        ),  # test speed -> dominance
        (
            3,
            7,
            [100] * 10,
            0,
            {(0, 7): 100, (7, 3): 100},
        ),  # test speed -> symmetry
        (
            3,
            7,
            [100] * 20,
            0,
            {(0, 7): 100, (7, 7): 100, (14, 6): 100},
        ),  # test speed -> symmetry
    ],
)
def test_staffing_cp_mnz_performance(
    min_len,
    max_len,
    estimated_rider_demand,
    expected_objective_value,
    num_expected_shifts_by_init_and_len,
):

    input_dict = {
        "min_len": min_len,
        "max_len": max_len,
        "rider_demand": estimated_rider_demand,
        "times": len(estimated_rider_demand),
    }

    model = CPShiftsMzn(input_data=input_dict)
    result = model.solve(model_file, timeout=4)

    assert result["slack_sum"] == expected_objective_value
    assert result["shifts"] == num_expected_shifts_by_init_and_len

    # only for version 1 and i am not exporting this -> in another test

    # symmetry assertions
    #     assert all(
    #         [
    #             t_s1 <= t_s2
    #             for t_s1, t_s2 in zip(
    #                 result.solution.starts_at[:-1], result.solution.starts_at[1:]
    #             )
    #         ]
    #     ), "starts_should be ordered to reduce options"

    #     assert all(
    #         [
    #             result.solution.length[i] >= result.solution.length[i + 1]
    #             for i in range(len(result.solution.length) - 1)
    #             if result.solution.starts_at[i] == result.solution.starts_at[i + 1]
    #         ]
    #     ), "if 2 shifts have same start then lenghts should be ordered desc"

    # else:
    #     assert (
    #         format_output_2(
    #             min_len=min_len, max_len=max_len, q_shifts=result.solution.q_shifts
    #         )
    #         == num_expected_shifts_by_init_and_len
    #     )


def tests_random_shifts():
    min_len = np.random.randint(1, 5)
    max_len = max(min_len, np.random.randint(1, 10))
    estimated_rider_demand = [
        np.random.randint(0, 20) for _ in range(np.random.randint(1, 10))
    ]

    input_dict = {
        "min_len": min_len,
        "max_len": max_len,
        "rider_demand": estimated_rider_demand,
        "times": len(estimated_rider_demand),
    }

    model = CPShiftsMzn(input_data=input_dict)
    result = model.solve(model_file, timeout=10)
    assert result["status"] != "UNSATISFIABLE"
