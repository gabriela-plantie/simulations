from scripts.shifts.create_shifts import CPShifts


def test_rider_demand_satisfaction():
    estimated_rider_demand = {0: 10, 1: 9, 2: 8}
    cp_shift = CPShifts(estimated_rider_demand)
    shifts = cp_shift.create_shifts(min_len=3, max_len=3)
    assert shifts == {(0, 3): 9, (3, 0): 1}  # 9 shifts of len 3 and startime 0
