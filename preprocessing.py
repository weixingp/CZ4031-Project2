import psycopg2

from config import db_user, db_host, db_password, db_port, db_name
from node import PlanNode


class QueryPlanner:
    """
    Query planner class
    """

    def __init__(self):
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
        self.aqp = []  # Stores list of root nodes to aqp trees

    def generate_plans(self, sql_query: str) -> None:
        """
        Generate 1 QEP and multiple AQPs
        Throws psycopg2.errors.SyntaxError if the sql query is invalid
        :param sql_query: The SQL query
        :return: None
        """
        self.__generate_qep(sql_query)
        self.__generate_aqps(sql_query)

    def __generate_qep(self, sql_query: str):
        """
        Generate QEP plan
        :param sql_query: The SQL query
        :return: None
        """
        constraints = self.__prepare_constraints_query()
        self.cursor.execute(f'{constraints} SET max_parallel_workers_per_gather = 0; EXPLAIN (VERBOSE, FORMAT JSON) ' + sql_query)
        self.conn.commit()
        plan = self.cursor.fetchall()
        # print(plan)
        self.qep = self.__build_tree_from_raw_plan(plan[0][0][0]["Plan"])

    def __generate_aqps(self, sql_query: str):
        constraints = self.__prepare_constraints_query(hash_join=False)
        self.cursor.execute(f'{constraints} SET max_parallel_workers_per_gather = 0; EXPLAIN (VERBOSE, FORMAT JSON) ' + sql_query)
        self.conn.commit()
        plan = self.cursor.fetchall()
        print(plan)
        self.aqp.append(self.__build_tree_from_raw_plan(plan[0][0][0]["Plan"]))

    @staticmethod
    def __prepare_constraints_query(
            hash_join=True,
            index_scan=True,
            merge_join=True,
            nest_loop=True,
            seq_scan=True,
            bitmap_scan=True
    ) -> str:
        """
        Generate the Planner Method Configuration query
        :return:
        """
        q = f"Set enable_hashjoin to {hash_join};" \
            f"Set enable_indexscan to {index_scan};" \
            f"Set enable_mergejoin to {merge_join};" \
            f"Set enable_nestloop to {nest_loop};" \
            f"Set enable_seqscan to {seq_scan};" \
            f"Set enable_bitmapscan to {bitmap_scan};"

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
        print("")
        def printTree(node, nodeInfo, indent=""):
            label, children = nodeInfo(node)
            print(indent[:-3] + "|_ " * bool(indent) + str(label))
            for more, child in enumerate(children, 1 - len(children)):
                childIndent = "|  " if more else "   "
                printTree(child, nodeInfo, indent + childIndent)

        print("Plan cost: ", root.cost)
        printTree(root, lambda n: (n.type, n.children))


if __name__ == '__main__':
    """
    Sample usage
    """

    sql = '''

    select l_orderkey, sum( l_extendedprice *( 1-l_discount )) as revenue,
    o_orderdate,
    o_shippriority
    from
        customer,
        orders,
        lineitem
    where
        c_mktsegment = 'HOUSEHOLD'
        and c_custkey = o_custkey
        and l_orderkey = o_orderkey
        and o_orderdate < date '1995-03-21' and l_shipdate > date '1955-03-21'
    group by
        l_orderkey,
        o_orderdate,
        o_shippriority
    order by
        revenue DESC,
        o_orderdate
        limit 10;
    '''

    qp = QueryPlanner()
    qp.generate_plans(sql)
    qp.print_plan_tree(qp.qep)
    qp.print_plan_tree(qp.aqp[0])
