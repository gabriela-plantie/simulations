from minizinc_tools.run_mnz_model import run_model
from minizinc_tools.transform_data_for_mnz_input import minizinc_input

model_file = "optimize_shift_creation/create_shifts_mnz.mnz"


def staffing_cp_mnz():
    with open(model_file, "r") as file:
        model_text = file.read()

    input_dict = {"min_len": 3, "max_len": 3}

    data_text = minizinc_input(input_dict)
    result = run_model(model_text=[model_text, data_text], verbose=True)
    print(result)
