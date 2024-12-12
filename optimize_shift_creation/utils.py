from collections import Counter


def format_output(t_shifts, len_shifts):
    return Counter([(t, l) for t, l in zip(t_shifts, len_shifts) if l > 0])
