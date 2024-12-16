from collections import Counter

from minizinc_tools.run_mnz_model import run_model
from minizinc_tools.transform_data_for_mnz_input import minizinc_input


class CPShiftsMzn:
    def __init__(self, input_data: dict):
        self.input_data = input_data

    def solve(self, model_file: str, timeout: int = 3):
        data_text = minizinc_input(self.input_data)
        with open(model_file, "r") as file:
            model_text = file.read()

        result = run_model(
            model_text=[model_text, data_text],
            timeout=timeout,
            verbose=True,
        )

        model_version = int(model_file.split("/")[-1].split(".")[0].split("_")[-1])
        return {
            "objective_value": result.objective,
            "slack_sum": result.solution.slack_sum,
            "shifts": self._format_output(result=result, model_version=model_version),
        }

    def _format_output(self, result, model_version):
        if model_version == 1:
            return self._format_output_1(result)
        elif model_version == 2:
            return self._format_output_2(result)
        else:
            raise NotImplementedError

    def _format_output_1(self, result):
        t_shifts = [t - 1 for t in result.solution.starts_at]
        len_shifts = result.solution.length
        return Counter([(t, l) for t, l in zip(t_shifts, len_shifts) if l > 0])

    def _format_output_2(self, result):
        min_len = self.input_data["min_len"]
        max_len = self.input_data["max_len"]
        q_shifts = result.solution.q_shifts
        return {
            (t, len): n
            for t, o in enumerate(q_shifts)
            for len, n in zip(range(min_len, max_len + 1), o)
            if n > 0
        }
