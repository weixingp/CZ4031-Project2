def sort_annotation(sort_keys: list) -> str:
    keys = ", ".join(sort_keys)
    description = f"Sort with the following sort keys: {keys}"
    reason = "Maybe no need a reason to sort"
    return description


def seq_scan_annotation(table_name: str, q_filter: str) -> str:

    description = "Tables are read using sequential scan."
    # todo: Reason copied from Mocha, rephrase it with our own words
    reason = f"Sequential scan on {table_name} is faster due to low selectivity of predicate {q_filter}."

    return f"{description} {reason}"


def extra_annotation(op: str, other_ops: list, reduction: float) -> str:
    text = f"{op} is faster than using {', '.join(other_ops)} here, " \
           f"and achieved a cost reduction by at least {'{:.1f}'.format(reduction)}x"

    return text
