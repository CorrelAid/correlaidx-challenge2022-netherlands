import csv
from collections import namedtuple
from pathlib import Path
from typing import Optional

from neo4j import GraphDatabase
from dotenv import dotenv_values

CONFIG = dotenv_values()
LeakNode = namedtuple("LeakNode", "searched_name,found_name,node_id,score")


def get_names(tx, names: Optional[list[str]] = None):
    if not names:
        names = Path(CONFIG["SEARCH_NAMES_FILE"]).read_text().splitlines()
    query = (
        'CALL db.index.fulltext.queryNodes("Everything_Names", $name) '
        'YIELD node, score '
        'RETURN node.name, node.node_id, score'
    )
    with open(CONFIG["SEARCH_OUTPUT_FULLTEXT"], "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter="|", )
        csv_writer.writerow(LeakNode._fields)
        for name in names:
            results = tx.run(query, name=name)
            csv_writer.writerows(LeakNode(name, *result.values()) for result in results)


def process_names(names: Optional[list[str]] = None, uri=CONFIG["NEO4J_URI"], user=CONFIG["NEO4J_USERNAME"],
                  password=CONFIG["NEO4J_PASSWORD"]):
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session(database="neo4j") as session:
            session.execute_read(get_names, names=names)


if __name__ == '__main__':
    process_names()
