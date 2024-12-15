from collections import Counter


def format_output(t_shifts, len_shifts):
    return Counter([(t, l) for t, l in zip(t_shifts, len_shifts) if l > 0])


def format_output_2(min_len, max_len, q_shifts):
    return {
        (t, len): n
        for t, o in enumerate(q_shifts)
        for len, n in zip(range(min_len, max_len + 1), o)
        if n > 0
    }
