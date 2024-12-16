import pytest

from optimize_shift_creation.create_shifts_mzn_cp import CPShiftsMzn
from optimize_shift_creation.create_shifts_ortools_cp import CPShifts


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


model_file = "optimize_shift_creation/create_shifts_mnz_1.mzn"
model_file = "optimize_shift_creation/create_shifts_mnz_2.mzn"


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
        (2, 3, [2, 2, 1, 2, 2], 0, {(0, 3): 1, (0, 2): 1, (3, 2): 2}),
        (1, 2, [2, 2], 0, {(0, 2): 2}),  # prioritize longer shifts
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
    ],
)
def test_staffing_cp_mnz(
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
    result = model.solve(model_file)

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
