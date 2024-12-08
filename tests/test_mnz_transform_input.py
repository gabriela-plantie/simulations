from minizinc.transform_data_for_mnz_input import minizinc_input

variables = {
    "n_days": 7,
    "days": range(7),
    "n_riders": 10,
    "l": [[1, 2], [2, 3], [3, 4]],
}


def test_str():
    assert minizinc_input({"s": "a"}) == "s = a;\n"


def test_str_array():
    assert (
        minizinc_input({"s": "array1d(LENGTH,[0,0,0])"})
        == "s = array1d(LENGTH,[0,0,0]);\n"
    )


def test_int():
    assert minizinc_input({"i": 3}) == "i = 3;\n"


def test_set():
    assert minizinc_input({"s": {3}}) == "s = {3};\n"


def test_set2():
    assert minizinc_input({"s": {1, 3}}) == "s = {1, 3};\n"


def test_range():
    assert minizinc_input({"r": range(2)}) == "r = [0, 1];\n"


def test_list():
    assert minizinc_input({"l": [1, 2, 3]}) == "l = [1, 2, 3];\n"


def test_list_of_strings_num():
    assert minizinc_input({"l": ["1", "2", "3"]}) == "l = [1, 2, 3];\n"


def test_list_of_strings_letters():
    assert minizinc_input({"l": ["a", "b", "c"]}) == "l = [a, b, c];\n"


def test_list_of_strings_mixed():
    assert minizinc_input({"l": ["a", 2, "c"]}) == "l = [a, 2, c];\n"


def test_list_of_sets():
    assert minizinc_input({"ls": [{1, 2}, {3, 4}]}) == "ls = [{1, 2}, {3, 4}];\n"


def test_list_of_lists_num():
    assert (
        minizinc_input({"ll": [[1, 2], [2, 3], [3, 4]]})
        == "ll = \n[| 1, 2\n | 2, 3\n | 3, 4\n |];\n"
    )


def test_list_of_lists_mixed():
    assert (
        minizinc_input({"ll": [[1, "b"], [2, 3], [3, 4]]})
        == "ll = \n[| 1, b\n | 2, 3\n | 3, 4\n |];\n"
    )


if __name__ == "__main__":
    print(minizinc_input(variables))
