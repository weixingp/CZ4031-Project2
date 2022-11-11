import psycopg2

from annotation import extra_annotation
from node import PlanNode


class QueryPlanner:
    """
    Query planner class
    """

    def __init__(self, db_host, db_port, db_name, db_user, db_password):
        """
        Init Query Planner
        Throws psycopg2.OperationalError if the connection to the db fails
        """
        self.conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )
        self.cursor = self.conn.cursor()

        self.qep: PlanNode = None  # The root node to the qep tree

        # AQP Stores alternative plans in dictionary
        # Dict format: {"Operation turned off": root node of the plan}
        # Eg: {"Hash Join": root} retrieves a plan without using Hash Join
        self.aqp = {}
        self.alt_plan_names = []  # Store keys to the plans

        # Extra annotations available for some operations
        # Compare performance between QEP and AQPs
        self.extra_annotation = {}

    def generate_plans(self, sql_query: str) -> None:
        """
        Generate 1 QEP and multiple AQPs
        Throws psycopg2.errors.SyntaxError if the sql query is invalid
        :param sql_query: The SQL query
        :return: None
        """
        # Reset variables
        self.qep = None
        self.aqp = {}
        self.alt_plan_names = []
        self.extra_annotation = {}

        # Generate plans
        self.__generate_qep(sql_query)
        self.__generate_aqps(sql_query)

    def __get_sql_query_plan(self, sql_query: str):
        try:
            self.cursor.execute(sql_query)
            self.conn.commit()
            plan = self.cursor.fetchall()
            return plan[0][0][0]["Plan"]
        except Exception as ex:
            self.conn.rollback()
            raise Exception(ex)

    def __generate_qep(self, sql_query: str):
        """
        Generate QEP plan
        :param sql_query: The SQL query
        :return: None
        """
        constraints = self.__prepare_constraints_query([])
        q = f'{constraints} SET max_parallel_workers_per_gather = 0; EXPLAIN (VERBOSE, FORMAT JSON) ' + sql_query
        plan = self.__get_sql_query_plan(q)
        self.qep = self.__build_tree_from_raw_plan(plan)

    def __generate_aqps(self, sql_query: str):
        """
        Generate AQPs by limiting 1 constraint at a time
        :param sql_query: The SQL query
        :return: None
        """
        assert self.qep, "QEP has to be generated first"

        join_types = ["Hash Join", "Nested Loop", "Merge Join"]
        scan_types = ["Seq Scan", "Bitmap Heap Scan", "Index Scan"]
        unique_types = PlanNode.get_unique_node_types(self.qep)

        # Generate AQP by limiting 1 operation type per plan
        for t in join_types + scan_types:
            if t in unique_types:
                constraints = self.__prepare_constraints_query([t])
                q = f'{constraints} SET max_parallel_workers_per_gather = 0; EXPLAIN (VERBOSE, FORMAT JSON) ' + sql_query
                plan = self.__get_sql_query_plan(q)
                root = self.__build_tree_from_raw_plan(plan)
                self.alt_plan_names.append(t)

                if t in join_types:
                    other_ops = [x for x in join_types if x != t]
                else:
                    other_ops = [x for x in scan_types if x != t]
                annotation = extra_annotation(op=t, other_ops=other_ops, reduction=root.cost/self.qep.cost)
                self.extra_annotation[t] = annotation
                self.aqp[t] = root

    @staticmethod
    def __prepare_constraints_query(off_list: list) -> str:
        """
        Generate the Planner Method Configuration query
        :param off_list: List of operations to turn off
        :return: sql statements
        """
        q = ""

        ops = {
            "Hash Join": "enable_hashjoin",
            "Index Scan": "enable_indexscan",
            "Merge Join": "enable_mergejoin",
            "Nest Loop": "enable_nestloop",
            "Seq Scan": "enable_seqscan",
            "Bitmap Heap Scan": "enable_bitmapscan"
        }

        for key, value in ops.items():
            if key in off_list:
                q += f"Set {value} to off;"
            else:
                q += f"Set {value} to on;"

        return q

    @staticmethod
    def __build_tree_from_raw_plan(plan: dict) -> PlanNode:
        """
        Build plan tree from the given plan
        :param plan: The plan
        :return: root node of the plan tree
        """

        def dfs(parent: PlanNode, p: list):
            if not p:
                return

            for item in p:
                node = PlanNode.create_node(plan=item)
                parent.children.append(node)
                if "Plans" in item:
                    dfs(node, item["Plans"])
                else:
                    continue

        root = PlanNode.create_node(plan=plan)
        if "Plans" in plan:
            dfs(root, plan["Plans"])

        return root

    @staticmethod
    def print_plan_tree(root: PlanNode) -> None:
        """
        Print plan tree in console
        :param root: Root of the plan
        :return: None
        """
        def printTree(node, nodeInfo, indent=""):
            label, children = nodeInfo(node)
            print(indent[:-3] + "|_ " * bool(indent) + str(label))
            for more, child in enumerate(children, 1 - len(children)):
                childIndent = "|  " if more else "   "
                printTree(child, nodeInfo, indent + childIndent)

        print("Plan cost: ", root.cost)
        printTree(root, lambda n: (n.type, n.children))
