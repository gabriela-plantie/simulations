import minizinc


def run_model(
    model_file=[], model_text=[], timeout=None, solver="gecode", verbose=False
):
    model = minizinc.Model()
    _solver = minizinc.Solver.lookup(solver)
    print(f"SOLVER: {_solver}")
    inst = minizinc.Instance(_solver, model)
    if len(model_file) > 0:
        for f in model_file:
            inst.add_file(f)
            inst.add_string("\n")
    if len(model_text) > 0:
        text = ""
        for t in model_text:
            text += t + "\n"

        # with open('./fede_test.mnz', 'w') as file:
        #     file.write(text)

        inst.add_string(text)
    # result = await inst.solve_async(timeout=timeout)
    result = inst.solve(timeout=timeout)
    if verbose:
        print("\n\n\n\n-----------------------------------------------------")
        print(result)
    return result
