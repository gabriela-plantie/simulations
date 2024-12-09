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
        # TODO improve this upper limit
        max_demand = max([demand for _, demand in self.rider_demand.items()])
        times = self.rider_demand.keys()
        total_times = max(times) - min(times) + 1
        max_area = total_times * max_demand
        max_shifts = {}
        for _len in np.arange(min_len, max_len + 1):
            max_shifts[int(_len)] = int(np.ceil(max_area / (1 * _len)))
        return max_shifts

        # create variables

    def create_shifts(self, max_len, min_len):
        max_shifts = self.get_shifts_len_possibilities(max_len=max_len, min_len=min_len)
        times = self.rider_demand.keys()

        print(f"Times: {list(times)}")
        print(f"Rider Demand: {self.rider_demand}")
        print(f"Max Shifts: {max_shifts}")

        max_total_shifts = int(max_shifts[min_len])

        model = cp_model.CpModel()

        # Arrays with one int per shift with the start time and length of the shift
        t_shifts, len_shifts = self.create_shift_variables(
            model=model,
            max_len=max_len,
            min_len=min_len,
            times=times,
            max_total_shifts=max_total_shifts,
        )

        # Array with one bool per shift per time stating if the shift was active
        active_shift_at_t = self.create_shift_active_in_each_t(
            model=model,
            times=times,
            max_total_shifts=max_total_shifts,
            t_shifts=t_shifts,
            len_shifts=len_shifts,
        )

        # Array with one bool per shift stating if the shift was ever active
        ever_active_shift = self.create_ever_active_shift(
            model=model,
            times=times,
            max_total_shifts=max_total_shifts,
            active_shift_at_t=active_shift_at_t,
        )

        # TODO una q diga q solo puede estar activo una vez
        # TODO q saque las simetrias
        # (para todos los shifts de igual longitud ordenar lexicograficamente)
        # TODO en casos de equivalencias
        # (2 shifts de 1 vs 1 shift de dos, tomar un criterio)
        # (esto se llama dominancia tambien?)

        # for debuggin purposes
        # model.Add(len_shifts[0] <= 3)
        # model.Add(len_shifts[0] >= 3)
        # model.Add(t_shifts[0] <= 0)
        # model.Add(t_shifts[0] >= 0)
        # model.Add(len_shifts[1] <= 2)
        # model.Add(len_shifts[1] >= 2)
        # model.Add(t_shifts[1] <= 0)
        # model.Add(t_shifts[1] >= 0)

        self.place_non_actives_shifts(
            model=model,
            times=times,
            max_total_shifts=max_total_shifts,
            t_shifts=t_shifts,
            len_shifts=len_shifts,
            ever_active_shift=ever_active_shift,
        )

        # enforce inside grid for active shifts!!!
        self.constraint_ever_active_shifts_inside_grid_time(
            model=model,
            times=times,
            t_shifts=t_shifts,
            len_shifts=len_shifts,
            max_total_shifts=max_total_shifts,
            ever_active_shift=ever_active_shift,
            min_len=min_len,
        )

        active_riders_in_t = self.create_active_riders_in_t(
            model=model,
            times=times,
            max_total_shifts=max_total_shifts,
            active_shift_at_t=active_shift_at_t,
        )

        # define slack var for each t
        slacks = self.create_slacks_for_demand_in_t(
            model=model, times=times, active_riders_in_t=active_riders_in_t
        )

        # creo el abs de la variable slack
        abs_slacks = self.create_abs_slacks_for_demand_in_t(
            times=times, model=model, slacks=slacks
        )

        objective = model.NewIntVar(
            lb=0,  # Valor absoluto siempre positivo
            ub=max(self.rider_demand) * len(times),
            name="objective",
        )
        model.Add(objective == sum(abs_slacks))
        model.Minimize(objective)

        solver = cp_model.CpSolver()

        solver.parameters.log_search_progress = True
        # solver.log_callback = print

        solution_printer = ConstraintInspector(len_shifts)
        status = solver.SolveWithSolutionCallback(model, solution_printer)

        # status = solver.Solve(model)
        print(f"objective reached: {solver.objective_value}")
        print(solver.StatusName(status))
        print(f"active riders in t :{[solver.value(r) for r in active_riders_in_t]}")
        print(f"slacks in t :{[solver.value(r) for r in slacks]}")
        print(f"abs slacks in t :{[solver.value(r) for r in abs_slacks]}")

        sol = self.format_output(
            solver=solver, t_shifts=t_shifts, len_shifts=len_shifts
        )
        return solver.objective_value, Counter(sol)

    def create_shift_variables(self, max_len, min_len, times, max_total_shifts, model):
        """
        Arrays with one int per shift with the start time and length of the shift.
        If lenght is 1 then the shift is only in one time slot.
        """
        time_out_of_bounds = max(times) + 1  # for shifts not used
        t_domain = list(
            set(
                [time_out_of_bounds]
                + list(range(min(times), max(max(times) - min_len + 2, 0)))
            )
        )
        t_domain.sort()
        print(f"t_domain {t_domain}")
        t_shifts = [
            model.NewIntVarFromDomain(
                domain=cp_model.Domain.FromValues(t_domain),
                name=f"t_for_shift_id_{s}",
            )
            for s in range(max_total_shifts)
        ]

        len_domain = list(set([0] + list(range(min_len, max_len + 1))))
        len_domain.sort()
        print(f"len_domain {len_domain}")
        len_shifts = [
            model.NewIntVarFromDomain(
                domain=cp_model.Domain.FromValues(len_domain),
                name=f"len_for_shift_id_{s}",
            )
            for s in range(max_total_shifts)
        ]

        return t_shifts, len_shifts

    def create_shift_active_in_each_t(
        self, times, max_total_shifts, model, t_shifts, len_shifts
    ):
        """
        Array with one bool per shift per time stating if the shift was active.
        """
        active_shift_at_t = {}

        for t in times:
            active_shift_at_t[t] = [
                model.NewBoolVar(name=f"is_active_shift_{s}_at_{t}")
                for s in range(max_total_shifts)
            ]

            # Add constraints to link activity to start time and length
            # A-> b1 y b2
            # no A -> !b1 y !b2
            for s, (shift_starts_at, shift_len) in enumerate(zip(t_shifts, len_shifts)):
                model.Add(shift_starts_at <= t).OnlyEnforceIf(active_shift_at_t[t][s])
                model.Add(shift_starts_at > t).OnlyEnforceIf(
                    active_shift_at_t[t][s].Not()
                )
                model.Add(t <= shift_starts_at + shift_len - 1).OnlyEnforceIf(
                    active_shift_at_t[t][s]
                )

        return active_shift_at_t

    def create_ever_active_shift(
        self, times, max_total_shifts, model, active_shift_at_t
    ):
        ever_active_shift = [
            model.NewBoolVar(name=f"ever_active_shift_{s}")
            for s in range(max_total_shifts)
        ]

        for s in range(max_total_shifts):
            model.AddBoolOr([active_shift_at_t[t][s] for t in times]).OnlyEnforceIf(
                ever_active_shift[s]
            )

            model.Add(sum([active_shift_at_t[t][s] for t in times]) == 0).OnlyEnforceIf(
                ever_active_shift[s].Not()
            )

        return ever_active_shift

    def constraint_ever_active_shifts_inside_grid_time(
        self,
        model,
        times,
        max_total_shifts,
        t_shifts,
        len_shifts,
        ever_active_shift,
        min_len,
    ):
        for s in range(max_total_shifts):
            model.Add(t_shifts[s] >= min(times)).OnlyEnforceIf(ever_active_shift[s])
            model.Add(len_shifts[s] > 0).OnlyEnforceIf(ever_active_shift[s])

            model.Add(t_shifts[s] + (len_shifts[s] - 1) <= max(times)).OnlyEnforceIf(
                ever_active_shift[s]
            )
            model.Add(t_shifts[s] + (min_len - 1) <= max(times)).OnlyEnforceIf(
                ever_active_shift[s]
            )

    def place_non_actives_shifts(
        self,
        times,
        max_total_shifts,
        model,
        t_shifts,
        len_shifts,
        ever_active_shift,
    ):
        """
        If the shift is not active then the start time and the length must be 0
        """
        for s in range(max_total_shifts):
            model.Add(len_shifts[s] == 0).OnlyEnforceIf(ever_active_shift[s].Not())

            model.Add(t_shifts[s] == max(times) + 1).OnlyEnforceIf(
                ever_active_shift[s].Not()
            )

    def create_active_riders_in_t(
        self, model, times, max_total_shifts, active_shift_at_t
    ):
        active_riders_in_t = [
            model.NewIntVar(
                lb=0,
                ub=self.rider_demand[t] * 2,  # improev this ub
                name=f"active_riders_in_{t}",
            )
            for t in times
        ]
        for t in times:
            model.Add(
                active_riders_in_t[t]
                == sum(active_shift_at_t[t][s] for s in range(max_total_shifts))
            ).with_name(f"c_active_riders_in_{t}")

        return active_riders_in_t

    # def create_times_acive_shift()
    def create_slacks_for_demand_in_t(self, times, model, active_riders_in_t):
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
        return slacks

    def create_abs_slacks_for_demand_in_t(self, times, model, slacks):
        abs_slacks = [
            model.NewIntVar(
                lb=0,  # Valor absoluto siempre positivo
                ub=self.rider_demand[t],  # Máximo posible (basado en la demanda)
                name=f"abs_slack_for_time_{t}",
            )
            for t in times
        ]
        for t in times:
            model.Add(abs_slacks[t] >= slacks[t])
            model.Add(abs_slacks[t] >= -slacks[t])
        return abs_slacks

    def format_output(self, t_shifts, len_shifts, solver):
        sol = list(
            zip(
                [solver.Value(s) for s in t_shifts],
                [solver.Value(s) for s in len_shifts],
            )
        )
        print(sol)
        return sol


class ConstraintInspector(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        super().__init__()
        self.__variables = variables

    def OnSolutionCallback(self):
        print("Solution found:")
        for var in self.__variables:
            print(f"{var.Name()} = {self.Value(var)}")
