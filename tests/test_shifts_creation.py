import pytest

from scripts.shifts.create_shifts import CPShifts


@pytest.mark.parametrize(
    "min_len, max_len, estimated_rider_demand, expected_shifts_by_init_and_len",
    [
        (3, 3, {0: 8, 1: 8, 2: 8}, {(0, 3): 8}),
        (3, 3, {0: 10, 1: 9, 2: 8}, {(0, 3): 9}),  # 9 shifts of len 3 and startime 0
        (2, 3, {0: 1, 1: 2, 2: 2}, {(0, 3): 1, (1, 2): 1}),
    ],
)
def test_rider_demand_satisfaction(
    min_len, max_len, estimated_rider_demand, expected_shifts_by_init_and_len
):

    cp_shift = CPShifts(estimated_rider_demand)
    shifts = cp_shift.create_shifts(min_len=min_len, max_len=max_len)
    assert {
        s: v for s, v in shifts.items() if s[1] > 0
    } == expected_shifts_by_init_and_len
