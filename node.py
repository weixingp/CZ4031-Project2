from annotation import *

supported_node_types = [
    "Sort",
    "Seq Scan",
    "Index Scan",
    "Bitmap Heap Scan",
    "Hash Join",
    "Merge Join",
    "Aggregate",
    "Hash",
    "Nested Loop",
    "Limit",
]


class PlanNode:
    """
    Base class for Plan nodes
    """
    type = "Base"

    def __init__(self, cost: float, row: int):
        self.cost = cost
        self.rows = row
        self.is_diff = False  # If this node is diff from another plan
        self.children: ["PlanNode"] = []

    def get_annotations(self):
        raise NotImplementedError

    def get_formatted_annotations(self):
        """
        Post process annotation
        """
        n = 12
        s = self.get_annotations()
        a = s.split()
        ret = ''
        for i in range(0, len(a), n):
            ret += ' '.join(a[i:i + n]) + '\n'

        return ret

    @classmethod
    def create_node(cls, plan: dict) -> "PlanNode":
        """
        Node factory
        :param plan: QEP from PostgresSQL
        :return:
        """
        node_type = plan["Node Type"]
        cost = plan["Total Cost"]
        rows = plan.get("Plan Rows", 0)
        if node_type == "Sort":

            return SortNode(cost=cost, row=rows, sort_keys=plan.get("Sort Key", "None"))
        elif node_type == "Seq Scan":
            return SeqScanNode(
                cost=cost,
                row=rows,
                table_name=plan.get("Relation Name", "None"),
                q_filter=plan.get("Filter", None),
            )
        elif node_type == "Index Scan":
            if "Index Cond" in plan:
                cond = plan["Index Cond"]
            elif "Filter" in plan:
                cond = plan["Filter"]
            else:
                cond = ""
            return IndexScanNode(
                cost=cost,
                row=rows,
                table_name=plan.get("Relation Name", "None"),
                cond=cond
            )
        elif node_type == "Bitmap Heap Scan":
            return BitMapHeapScanNode(cost=cost, row=rows, table_name=plan.get("Relation Name", "None"))
        elif node_type == "Hash Join":
            return HashJoinNode(cost=cost, row=rows, cond=plan.get("Hash Cond", ""))
        elif node_type == "Merge Join":
            return MergeJoinNode(cost=cost, row=rows, cond=plan.get("Merge Cond", ""))
        elif node_type == "Aggregate":
            group_key = plan["Group Key"] if "Group Key" in plan else "None"
            return AggregateNode(cost=cost, row=rows, group_keys=group_key)
        elif node_type == "Hash":
            return HashNode(cost=cost, row=rows)
        elif node_type == "Nested Loop":
            return NestedLoop(cost=cost, row=rows)
        elif node_type == "Limit":
            return LimitNode(cost=cost, row=rows)
        else:
            return UndefinedNode(cost=cost, row=rows, type_name=plan["Node Type"])

    @classmethod
    def get_unique_node_types(cls, root: "PlanNode") -> list:
        """
        Get a list of unique node types used in a plan tree
        :param root: The root node
        :return: list of node types
        """
        lst = set()

        def dfs(n: "PlanNode"):
            lst.add(n.type)
            for item in n.children:
                dfs(item)

        dfs(root)
        return list(lst)

    @classmethod
    def compare_trees(cls, org: "PlanNode", alt: "PlanNode"):
        """
        Compare 2 trees, mark a node if it's different from the first
        """
        def dfs_mark(node):
            """
            Mark all child as diff
            """
            node.is_diff = True
            for n in node.children:
                dfs_mark(n)

        def dfs_compare(node1, node2):
            """
            Compare two trees recursively
            """
            if not node1 and node2:
                # node 2 must be all diff below
                dfs_mark(node2)

            if node1 and not node2:
                # nth to compare
                return

            if not node1 and not node2:
                # nth to compare
                return

            if node1.type != node2.type:
                # Diff
                dfs_mark(node2)
            else:
                if len(node1.children) == 2:
                    left1 = node1.children[0]
                    left2 = node1.children[1]
                elif len(node1.children) == 1:
                    left1 = node1.children[0]
                    left2 = None
                else:
                    left1 = None
                    left2 = None

                if len(node2.children) == 2:
                    right1 = node2.children[0]
                    right2 = node2.children[1]
                elif len(node2.children) == 1:
                    right1 = node2.children[0]
                    right2 = None
                else:
                    right1 = None
                    right2 = None

                dfs_compare(left1, right1)
                dfs_compare(left2, right2)

        dfs_compare(org, alt)


class SortNode(PlanNode):
    type = "Sort"

    def __init__(self, cost: float, row: int, sort_keys: list):
        """
        Sort node
        :param cost: Total cost
        :param sort_keys: list of sort keys
        """
        super().__init__(cost, row)
        self.sort_keys = sort_keys

    def get_annotations(self) -> str:
        text = sort_annotation(self.sort_keys)

        return text


class SeqScanNode(PlanNode):
    type = "Seq Scan"

    def __init__(self, cost: float, row: int, table_name: str, q_filter: str):
        """
        Sequential scan node
        :param cost: Total cost
        :param table_name: The table name the scan is run on
        :param q_filter: The filter the scan is run on
        """
        super().__init__(cost, row)
        self.table_name = table_name
        self.q_filter = q_filter

    def get_annotations(self) -> str:
        text = seq_scan_annotation(self.table_name, self.q_filter, self.rows)
        return text


class IndexScanNode(PlanNode):
    type = "Index Scan"

    def __init__(self, cost: float, row: int, table_name: str, cond: str):
        """
        Index Scan node
        :param cost: Total cost
        :param table_name: The table name the scan is run on
        :param cond: The condition of the scan is run on
        """
        super().__init__(cost, row)
        self.table_name = table_name
        self.cond = cond

    def get_annotations(self) -> str:
        text = index_scan_annotation(self.table_name, self.cond)
        return text


class BitMapHeapScanNode(PlanNode):
    type = "Bitmap Heap Scan"

    def __init__(self, cost: float, row: int, table_name: str):
        """
        Index Scan node
        :param cost: Total cost
        :param table_name: The table name the scan is run on
        """
        super().__init__(cost, row)
        self.table_name = table_name

    def get_annotations(self) -> str:
        text = bit_map_heap_scan_annotation(self.table_name)
        return text


class HashJoinNode(PlanNode):
    type = "Hash Join"

    def __init__(self, cost: float, row: int, cond: str):
        """
        Hash Join node
        :param cost: Total cost
        :param cond: The condition of the join is run on
        """
        super().__init__(cost, row)
        self.cond = cond

    def get_annotations(self) -> str:
        text = hash_join_annotation(self.cond)
        return text


class MergeJoinNode(PlanNode):
    type = "Merge Join"

    def __init__(self, cost: float, row: int, cond: str):
        """
        Merge Join node
        :param cost: Total cost
        :param cond: The condition of the join is run on
        """
        super().__init__(cost, row)
        self.cond = cond

    def get_annotations(self) -> str:
        text = merge_join_annotation(self.cond)
        return text


class AggregateNode(PlanNode):
    type = "Aggregate"

    def __init__(self, cost: float, row: int, group_keys: list):
        """
        Aggregate scan node
        :param cost: Total cost
        :param group_keys: List group by keys
        """
        super().__init__(cost, row)
        self.group_keys = group_keys

    def get_annotations(self) -> str:
        text = aggregate_annotation(self.group_keys)
        return text


class HashNode(PlanNode):
    type = "Hash"

    def __init__(self, cost: float, row: int):
        """
        Hash node
        :param cost: Total cost
        """
        super().__init__(cost, row)

    def get_annotations(self) -> str:
        text = hash_annotation()
        return text


class NestedLoop(PlanNode):
    type = "Nested Loop"

    def __init__(self, cost: float, row: int):
        """
        Nested Loop node
        :param cost: Total cost
        """
        super().__init__(cost, row)

    def get_annotations(self) -> str:
        text = nested_loop_annotation()
        return text


class LimitNode(PlanNode):
    type = "Limit"

    def __init__(self, cost: float, row: int):
        """
        Limit node
        :param cost: Total cost
        """
        super().__init__(cost, row)

    def get_annotations(self) -> str:
        text = limit_annotation()
        return text


class UndefinedNode(PlanNode):
    type = "Undefined Node"

    def __init__(self, cost: float, row: int, type_name: str = "Undefined Node"):
        """
        Limit node
        :param cost: Total cost
        """
        super().__init__(cost, row)
        self.type = type_name

    def get_annotations(self) -> str:
        return ""
