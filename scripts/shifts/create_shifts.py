from collections import Counter

import numpy as np
from ortools.sat.python import cp_model


class CPShifts:

    def __init__(self, estimated_rider_demand):
        self.rider_demand = estimated_rider_demand
        self.rider_demand_t = self.convert_rider_demand_to_array()

    def convert_rider_demand_to_array(self):
        times = self.rider_demand.keys()
        return [
            self.rider_demand[t] if t in times else 0 for t in range(max(times) + 1)
        ]

    def get_shifts_len_possibilities(self, max_len, min_len):
        # ESTA MAL!!!!
        # create max number of shifts of each type
        max_demand = max([demand for _, demand in self.rider_demand.items()])
        times = self.rider_demand.keys()
        total_times = max(times) - min(times) + 1
        max_area = total_times * max_demand
        max_shifts = {}
        for _len in np.arange(min_len, max_len + 1):
            max_shifts[_len] = max(max_demand, np.ceil(max_area / (_len * 1)))
        return max_shifts

        # create variables

    def create_shifts(self, max_len, min_len):
        max_shifts = self.get_shifts_len_possibilities(max_len=max_len, min_len=min_len)
        model = cp_model.CpModel()
        times = self.rider_demand.keys()

        print(f"Times: {list(times)}")
        print(f"Rider Demand: {self.rider_demand}")
        print(f"Max Shifts: {max_shifts}")

        max_total_shifts = int(max_shifts[min_len])

        t_shifts = [
            model.NewIntVar(
                lb=min(times),
                ub=max(max(times) - min_len, min_len),
                name=f"t_for_shift_id_{s}",
            )
            for s in range(max_total_shifts)
        ]

        len_domain = [0] + list(range(min_len, max_len + 1))
        len_shifts = [
            model.NewIntVarFromDomain(
                domain=cp_model.Domain.FromValues(len_domain),
                name=f"len_for_shift_id_{s}",
            )
            for s in range(max_total_shifts)
        ]

        # active_riders_in_t = [
        #     sum([
        #         1 for t_ini, _len in zip(t_shifts, len_shifts)
        #         if  ((t_ini <= t) and (t < (t_ini + _len)))
        #         ])
        #     for t in times
        #     ]

        active_riders_in_t = []
        for t in times:
            # Boolean variables for active shifts at time t
            active_shifts_at_t = [
                model.NewBoolVar(name=f"is_active_shift_{s}_at_{t}")
                for s in range(max_total_shifts)
            ]

            # Add constraints to link activity to start time and length
            for s, (t_ini, _len) in enumerate(zip(t_shifts, len_shifts)):
                model.Add(t_ini <= t).OnlyEnforceIf(active_shifts_at_t[s])
                model.Add(t < t_ini + _len).OnlyEnforceIf(active_shifts_at_t[s])

                # Create Boolean variables for the conditions
                t_ini_le_t = model.NewBoolVar(f"t_ini_le_t_{s}_{t}")
                t_lt_t_ini_plus_len = model.NewBoolVar(f"t_lt_t_ini_plus_len_{s}_{t}")

                # Link constraints to Boolean variables
                model.Add(t_ini <= t).OnlyEnforceIf(t_ini_le_t)
                model.Add(t_ini > t).OnlyEnforceIf(t_ini_le_t.Not())

                model.Add(t < t_ini + _len).OnlyEnforceIf(t_lt_t_ini_plus_len)
                model.Add(t >= t_ini + _len).OnlyEnforceIf(t_lt_t_ini_plus_len.Not())

                # Combine the Boolean variables into a composite condition
                combined_condition = model.NewBoolVar(f"combined_condition_{s}_{t}")
                model.AddBoolAnd([t_ini_le_t, t_lt_t_ini_plus_len]).OnlyEnforceIf(
                    combined_condition
                )

                # Add the "if and only if" relationship
                model.Add(active_shifts_at_t[s] == combined_condition)

            active_riders_in_t.append(sum(active_shifts_at_t))

            for s in range(max_total_shifts):
                # Enforce len_shifts[s] == 0 if the shift is not active
                model.Add(len_shifts[s] == 0).OnlyEnforceIf(active_shifts_at_t[s].Not())

                # Alternatively, enforce len_shifts[s] >= 1 only if the shift is active
                model.Add(len_shifts[s] >= 1).OnlyEnforceIf(active_shifts_at_t[s])

        # define slack var for each t
        slacks = [
            model.NewIntVar(
                lb=-self.rider_demand[t],
                ub=+self.rider_demand[t],
                name=f"slack_for_time_{t}",
            )
            for t in times
        ]
        for t in times:
            model.Add(active_riders_in_t[t] + slacks[t] == self.rider_demand[t])

        # creo el abs de la variable slack
        abs_slacks = [
            model.NewIntVar(
                lb=0,  # Valor absoluto siempre positivo
                ub=self.rider_demand[t],  # Máximo posible (basado en la demanda)
                name=f"abs_slack_for_time_{t}",
            )
            for t in times
        ]
        for t in times:
            # Modelo del valor absoluto
            model.Add(abs_slacks[t] >= slacks[t])
            model.Add(abs_slacks[t] >= -slacks[t])

        objective = sum(abs_slacks)

        model.Minimize(objective)
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        print(solver.StatusName(status))
        sol = list(
            zip(
                [solver.Value(s) for s in t_shifts],
                [solver.Value(s) for s in len_shifts],
            )
        )
        return Counter(sol)
        1

        # # {long 3: [3,4,8]} # a que hora empieza cada uno
        # start_time_of_shifts_by_type = {}
        # for _len, q in max_shifts.items():
        #     start_time_of_shifts_by_type[_len] = {}
        #     for i in range(q):
        #         start_time_of_shifts_by_type[_len][i] = model.new_int_var(
        #             lb=min(times),
        #             ub=max(times) + 1, # the last one is outside
        #             name=f"t_for_shift-id_{i}_with_len_{_len}")

        # shifts_by_time = {}
        # for t in range(times):
        #     shifts_by_time[t] = {}
        #     for _len in range(min_len, max_len+1):
        #         model.new_int_var(
        #             lb=0,
        #             ub=max_shifts[_len],
        #             name=f"num_shifts_in_t_{t}_with_len_{_len}")

    # minizinc
    # constraint cumulative(x, size, size, height);
    # constraint cumulative(y, size, size, width);

    # ortools
    # Adds Cumulative(intervals, demands, capacity).
    # for all t: sum(demands[i] if (start(intervals[i]) <= t < end(intervals[i]))
    # and (intervals[i] is present)) <= capacity
    # capacity = demanda en t, pero no veo capacity en t

    # x[s1] + size[s1] <= x[s2] \/  # s2 esta a la derecha
    # x[s2] + size[s2] <= x[s1] \/  # o S1 esta a la derecha
    # use a cumulative constraint
