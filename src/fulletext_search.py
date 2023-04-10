import csv
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Callable, Optional

from dotenv import dotenv_values
from neo4j import GraphDatabase
from rapidfuzz.fuzz import token_set_ratio
from rapidfuzz.process import extract

CONFIG = dotenv_values()
LeakNode = namedtuple("LeakNode", "searched_name,found_name,node_id,score")


def fulltext_search(tx, names: Optional[list[str]] = None) -> None:
    """
    The transactions to search the database are performed here and written to
    a csv file.

    :param tx: The database session to use for searching
    :param names: Optional list of names to search for
    """
    if not names:
        names = Path(CONFIG["SEARCH_NAMES_FILE"]).read_text().splitlines()
    query = (
        'CALL db.index.fulltext.queryNodes("Everything_Names", $name) '
        'YIELD node, score '
        'RETURN node.name, node.node_id, score'
    )

    with open(CONFIG["SEARCH_OUTPUT"], "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter="|", )
        csv_writer.writerow(LeakNode._fields)
        for name in names:
            results = tx.run(query, name=name)
            csv_writer.writerows(LeakNode(name, *result.values()) for result in results)


def fuzzy_match_search(tx, names: Optional[list[str]] = None) -> None:
    if not names:
        names = Path(CONFIG["SEARCH_NAMES_FILE"]).read_text().splitlines()
    node_attrs = {"node.name", "node.original_name", "node.former_name", "node.company_name", "node.node_id"}
    query = (
        "MATCH (node) WHERE node.name IS NOT NULL "
        f"RETURN {', '.join(node_attrs)}"
    )
    found_names = defaultdict(set)
    results = tx.run(query)
    for item in results:
        for attr in node_attrs:
            if attr != "node.node_id" and item[attr] is not None:
                found_names[item[attr]].add(item["node.node_id"])

    with open(CONFIG["SEARCH_OUTPUT"], "a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter="|", )
        csv_writer.writerow(LeakNode._fields)

        for name in names:
            results = extract(name, found_names.keys(), scorer=token_set_ratio, score_cutoff=75, )
            csv_writer.writerows(results)


def process_names(get_names: Callable, names: Optional[list[str]] = None, uri=CONFIG["NEO4J_URI"],
                  user=CONFIG["NEO4J_USERNAME"], password=CONFIG["NEO4J_PASSWORD"]) -> None:
    """
    Search for names using a fulltext index in Neo4J. This function sets up
    the driver and session for interacting with the database.

    Names can optionally be passed directly to this function for search, or
    add to a file that will be read in the actual search function.

    :param get_names: Function to use for searching names
    :param names: Optional list of names to search for
    :param uri: URI to connect to the database
    :param user: The username for connecting to the database
    :param password: The password that goes with the username
    """
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session(database="neo4j") as session:
            session.execute_read(get_names, names=names)


if __name__ == '__main__':
    process_names(fuzzy_match_search)
