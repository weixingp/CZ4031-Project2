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
    description = f"Sort with the following sort keys: {keys}"
    return description


def seq_scan_annotation(table_name: str, q_filter: str) -> str:

    description = "Tables are read using sequential scan."
    reason = f"Sequential scan on {table_name} is faster due to low selectivity of predicate {q_filter}."
    return f"{description} {reason}"


def bit_map_heap_scan_annotation(table_name: str) -> str:

    description = "Tables are read using Bitmap heap scan."
    reason = f"Bitmap heap scan on {table_name} is faster here. Use of a bitmap scan" \
             f"allows the optimizer to generate a plan that can take advantage" \
             f"of multiple indexes to match up different portions of the query"
    return f"{description} {reason}"


def index_scan_annotation(table_name: str, cond: str) -> str:

    description = "Tables are read using index scan."
    reason = f"index scan on {table_name} is implemented as it use index on  {cond}."
    return f"{description} {reason}"


def hash_join_annotation(cond: str, q_filter: str) -> str:

    description = "Hash Join is used on {cond}."
    reason = f"Hash join is efficient for processing large, " \
             f"unsorted and non-indexed inputs compared to other join types.In this query," \
             f" it has better performance when doing equality join where hash condition is {q_filter}"
    return f"{description} {reason}"


def merge_join_annotation() -> str:

    description = "Merge Join is used."
    reason = f"merge join is implemented as it the involved relations " \
             f"are both too big for a hash that fits"
    return f"{description} {reason}"


def aggregate_annotation(group_keys:list) -> str:

    description = "Aggregation is performed here."
    reason = f"Aggregation is performed on {group_keys}."
    return f"{description} {reason}"


# revise below
def hash_annotation() -> str:
    description = "hash is implemented "
    return f"{description}"


def nested_loop_annotation() -> str:
    description = "nested loop is implemented "
    reason = "Nested loop joins are ideal when one join is smaller and" \
             " the other join input is large and indexed on its join columns"
    return f"{description} {reason}"


def limit_annotation() -> str:
    description = "limit is implemented "
    return f"{description}"


def undefined_annotation() -> str:
    description = "undefined Node found"
    return f"{description}"
