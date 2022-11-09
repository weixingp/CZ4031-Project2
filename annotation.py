def template_annotation() -> str:
    description = ""
    reason = f""

    return f"{description} {reason}"

def sort_annotation(sort_keys: list) -> str:
    keys = ", ".join(sort_keys)
    description = f"Sort with the following sort keys: {keys}"
    reason = "Maybe no need a reason to sort"
    return description


def seq_scan_annotation(table_name: str, q_filter: str) -> str:

    description = "Tables are read using sequential scan."
    reason = f"Sequential scan on {table_name} is faster due to low selectivity of predicate {q_filter}."

    return f"{description} {reason}"


def index_scan_annotation(table_name: str, cond: str) -> str:

    description = "Tables are read using index scan."
    reason = f"index scan on {table_name} is implemented as it use index on  {cond}."

    return f"{description} {reason}"


def hash_join_annotation(cond: str) -> str:

    description = "Hash Join is used."
    reason = f"hash join is implemented because of {cond}."

    return f"{description} {reason}"


def aggregate_annotation(group_keys:list) -> str:

    description = "Aggregation is performed here."
    reason = f"Aggregation is performed on {group_keys}."

    return f"{description} {reason}"


# revise below
def hash_annotation() -> str:

    description = "hash is implemented here"
    reason = f"Maybe no need a reason to sort"

    return f"{description} {reason}"


def template_annotation() -> str:
    description = ""
    reason = f""

    return f"{description} {reason}"





