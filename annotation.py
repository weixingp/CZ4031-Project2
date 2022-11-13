def extra_annotation(op: str, other_ops: list, reduction: float) -> str:
    text = f"{op} is faster than using {', '.join(other_ops)} here, " \
           f"and achieved a cost reduction by at least {'{:.1f}'.format(reduction)}x"
    return text


def template_annotation() -> str:
    description = ""
    reason = f""
    return f"{description} {reason}"


def sort_annotation(sort_keys: list) -> str:
    keys = ", ".join(sort_keys)
    description = f"Sorts rows into an order, with the following sort keys: {keys}"
    return description


def seq_scan_annotation(table_name: str, q_filter: str, rows: int) -> str:
    description = f"Reads the rows from {table_name} table, in order."
    if q_filter:
        reason = f"Sequential scan on {table_name} is faster due to low selectivity of predicate {q_filter}."
    else:
        if rows == 1:
            reason = f"Sequential scan on {table_name} is faster to get a row from a small table."
        else:
            reason = f"Sequential scan on {table_name} is faster to get " \
                     f"a high proportion of the rows from larger tables."
    return f"{description} {reason}"


def bit_map_heap_scan_annotation(table_name: str) -> str:
    description = f"Reads pages from a bitmap created by the other operations on {table_name} table, filtering out any " \
                  "rows that don't match the condition. "
    reason = f"Bitmap heap scan on {table_name} is faster here. Use of a bitmap scan" \
             f"allows the optimizer to generate a plan that can take advantage" \
             f"of multiple indexes to match up different portions of the query"
    return f"{description} {reason}"


def index_scan_annotation(table_name: str, cond: str) -> str:
    description = f"Scans the index for rows which match a particular condition, then reads them from {table_name} table."
    reason = f"Index scan on {table_name} is faster because only a small proportion of the rows is needed and an " \
             f"index is created on {cond}. "
    return f"{description} {reason}"


def hash_join_annotation(cond: str) -> str:
    description = f"Hash Join is performed on {cond}."
    reason = f"Hash join is efficient for processing large, " \
             f"unsorted and non-indexed inputs compared to other join types. In this query," \
             f" it has better performance when doing equality join where hash condition is {cond}"
    return f"{description} {reason}"


def merge_join_annotation(cond: str) -> str:
    description = f"Merge Join is is performed on {cond}."
    reason = f"Merge join is used on {cond} as it the involved relations " \
             f"are both too big for a hash that fits"
    return f"{description} {reason}"


def aggregate_annotation(group_keys: list) -> str:
    description = f"Aggregation is performed on {group_keys}"
    reason = ""
    return f"{description} {reason}"


# revise below
def hash_annotation() -> str:
    description = "Hash is performed."
    return f"{description}"


def nested_loop_annotation() -> str:
    description = "Nested loop is performed."
    reason = "Nested loop joins are ideal when one join is smaller and" \
             " the other join input is large and indexed on its join columns"
    return f"{description} {reason}"


def limit_annotation() -> str:
    description = "Limit is performed."
    return f"{description}"


def undefined_annotation() -> str:
    description = ""
    return f"{description}"
