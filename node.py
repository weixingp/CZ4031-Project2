from annotation import sort_annotation, seq_scan_annotation

supported_node_types = [
    "Sort",
    "Seq Scan",
    "Index Scan",
    "Hash Join",
    "Aggregate",
    "Hash",
    "Nested Loop",
    "Limit",
    "Merge Join"
]


class PlanNode:
    """
    Base class for Plan nodes
    """
    type = "Base"

    def __init__(self, cost: float):
        self.cost = cost

        self.children: ["PlanNode"] = []

    def get_annotations(self):
        raise NotImplementedError

    @classmethod
    def create_node(cls, plan: dict) -> "PlanNode":
        """
        Node factory
        :param plan: QEP from PostgresSQL
        :return:
        """
        node_type = plan["Node Type"]
        cost = plan["Total Cost"]

        if node_type == "Sort":
            return SortNode(cost=cost, sort_keys=plan["Sort Key"])
        elif node_type == "Seq Scan":
            if "Filter" in plan:
                f = plan["Filter"]
            else:
                f = "()"
            return SeqScanNode(cost=cost, table_name=plan["Relation Name"], q_filter=f)
        elif node_type == "Index Scan":

            if "Index Cond" in plan:
                cond = plan["Index Cond"]
            elif "Filter" in plan:
                cond = plan["Filter"]
            else:
                cond = ""

            return IndexScanNode(cost=cost, table_name=plan["Relation Name"], cond=cond)
        elif node_type == "Hash Join":
            return HashJoinNode(cost=cost, cond=plan["Hash Cond"])
        elif node_type == "Merge Join":
            return MergeJoinNode(cost=cost, cond=plan["Merge Cond"])
        elif node_type == "Aggregate":
            return AggregateNode(cost=cost, group_keys=plan["Group Key"])
        elif node_type == "Hash":
            return HashNode(cost=cost)
        elif node_type == "Nested Loop":
            return NestedLoop(cost=cost)
        elif node_type == "Limit":
            return LimitNode(cost=cost)
        else:
            return UndefinedNode(cost=cost, type_name=plan["Node Type"])


class SortNode(PlanNode):
    type = "Sort"

    def __init__(self, cost: float, sort_keys: list):
        """
        Sort node
        :param cost: Total cost
        :param sort_keys: list of sort keys
        """
        super().__init__(cost)
        self.sort_keys = sort_keys

    def get_annotations(self) -> str:
        text = sort_annotation(self.sort_keys)

        return text


class SeqScanNode(PlanNode):
    type = "Seq Scan"

    def __init__(self, cost: float, table_name: str, q_filter: str):
        """
        Sequential scan node
        :param cost: Total cost
        :param table_name: The table name the scan is run on
        :param q_filter: The filter the scan is run on
        """
        super().__init__(cost)
        self.table_name = table_name
        self.q_filter = q_filter

    def get_annotations(self) -> str:
        text = seq_scan_annotation(self.table_name, self.q_filter)
        return text


class IndexScanNode(PlanNode):
    type = "Index Scan"

    def __init__(self, cost: float, table_name: str, cond: str):
        """
        Index Scan scan node
        :param cost: Total cost
        :param table_name: The table name the scan is run on
        :param cond: The condition of the scan is run on
        """
        super().__init__(cost)
        self.table_name = table_name
        self.cond = cond

    def get_annotations(self) -> str:
        text = ""
        return text


class HashJoinNode(PlanNode):
    type = "Hash Join"

    def __init__(self, cost: float, cond: str):
        """
        Hash Join node
        :param cost: Total cost
        :param cond: The condition of the join is run on
        """
        super().__init__(cost)
        self.cond = cond

    def get_annotations(self) -> str:
        text = ""
        return text


class MergeJoinNode(PlanNode):
    type = "Merge Join"

    def __init__(self, cost: float, cond: str):
        """
        Merge Join node
        :param cost: Total cost
        :param cond: The condition of the join is run on
        """
        super().__init__(cost)
        self.cond = cond

    def get_annotations(self) -> str:
        text = ""
        return text


class AggregateNode(PlanNode):
    type = "Aggregate"

    def __init__(self, cost: float, group_keys: list):
        """
        Aggregate scan node
        :param cost: Total cost
        :param group_keys: List group by keys
        """
        super().__init__(cost)
        self.group_keys = group_keys

    def get_annotations(self) -> str:
        text = ""
        return text


class HashNode(PlanNode):
    type = "Hash"

    def __init__(self, cost: float):
        """
        Hash node
        :param cost: Total cost
        """
        super().__init__(cost)

    def get_annotations(self) -> str:
        text = ""
        return text


class NestedLoop(PlanNode):
    type = "Nested Loop"

    def __init__(self, cost: float):
        """
        Nested Loop node
        :param cost: Total cost
        """
        super().__init__(cost)

    def get_annotations(self) -> str:
        text = ""
        return text


class LimitNode(PlanNode):
    type = "Limit"

    def __init__(self, cost: float):
        """
        Limit node
        :param cost: Total cost
        """
        super().__init__(cost)

    def get_annotations(self) -> str:
        text = ""
        return text


class UndefinedNode(PlanNode):
    type = "Undefined Node"

    def __init__(self, cost: float, type_name: str = "Undefined Node"):
        """
        Limit node
        :param cost: Total cost
        """
        super().__init__(cost)
        self.type = type_name

    def get_annotations(self) -> str:
        text = ""
        return text
