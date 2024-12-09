def transform_list(var):
    if isinstance(var[0], list):
        return (
            "\n[| " + "\n | ".join(map(lambda x: ", ".join(map(str, x)), var)) + "\n |]"
        )
    return "[" + ", ".join(map(str, var)) + "]"


def minizinc_input(vars):
    transform = {
        str: str,
        int: str,
        set: str,
        range: lambda r: "[" + ", ".join(map(str, r)) + "]",
        list: transform_list,
    }

    txt = ""
    for k, v in vars.items():
        txt += k + " = " + transform[type(v)](v) + ";\n"

    return txt
