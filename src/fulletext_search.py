from collections import namedtuple

from neo4j import GraphDatabase
from dotenv import dotenv_values

CONFIG = dotenv_values()
LeakNode = namedtuple("LeakNode", "name,node_id,score")


def get_names(tx, names):
    query = (
        'CALL db.index.fulltext.queryNodes("Everything_Names", $name) '
        'YIELD node, score '
        'RETURN node.name, node.node_id, score'
    )
    nodes = set()
    for name in names:
        results = tx.run(query, name=name)
        nodes.update(LeakNode(*result.values()) for result in results)
    return nodes


def process_names(names, uri=CONFIG["NEO4J_URI"], user=CONFIG["NEO4J_USERNAME"], password=CONFIG["NEO4J_PASSWORD"]):
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session(database="neo4j") as session:
            results = session.execute_read(get_names, names=names)
            print("c")


if __name__ == '__main__':
    process_names(["Macadam", "iQor"])
