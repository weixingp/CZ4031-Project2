sql1 = """
select
	c_count,
	count(*) as custdist
from
	(
		select
			c_custkey,
			count(o_orderkey)
		from
			customer left outer join orders on
				c_custkey = o_custkey
		group by
			c_custkey
	) as c_orders (c_custkey, c_count)
group by
	c_count
order by
	custdist,
	c_count
limit 1;
"""

sql2 = """
select
	c_custkey,
	count(o_orderkey)
from
	customer, orders
where 
	c_custkey = o_custkey
	and c_acctbal > 9000
	and c_mktsegment = 'AUTOMOBILE'
	and o_orderpriority = '1-URGENT'
group by
	c_custkey
"""

sql3 = """
    select
        sum(l_extendedprice * l_discount) as revenue
      from
        lineitem
      where
        l_extendedprice > 100;
"""

sql4 = """
select
	ps_partkey,
	sum(ps_supplycost * ps_availqty) as value
from
	partsupp,
	supplier,
	nation
where
	ps_suppkey = s_suppkey
	and s_nationkey = n_nationkey
	and n_name = 'INDIA'
group by
	ps_partkey having
		sum(ps_supplycost * ps_availqty) > (
			select
				sum(ps_supplycost * ps_availqty)
			from
				partsupp,
				supplier,
				nation
			where
				ps_suppkey = s_suppkey
				and s_nationkey = n_nationkey
				and n_name = 'INDIA'
		)
order by
	value desc
limit 1;
"""

sql_list = [sql1, sql2, sql3, sql4]
