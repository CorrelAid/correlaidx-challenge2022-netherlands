import csv
from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Iterable, Optional

from dotenv import dotenv_values
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from rapidfuzz.fuzz import token_set_ratio
from rapidfuzz.process import extract

CONFIG = dotenv_values()
LeakNode = namedtuple("LeakNode", "searched_name,found_name,node_id,score")


class NameSearchNeo4J(ABC):
    def __init__(self, search_names: Optional[Iterable[str]] = None):
        if not search_names:
            search_names = Path(CONFIG["SEARCH_NAMES_FILE"]).read_text().splitlines()
        self.search_names: Iterable[str] = search_names

    def get_names(self, uri=CONFIG["NEO4J_URI"], user=CONFIG["NEO4J_USERNAME"],
                      password=CONFIG["NEO4J_PASSWORD"]) -> None:
        """
        Search for names using a fulltext index in Neo4J. This function sets up
        the driver and session for interacting with the database.

        Names can optionally be passed directly to this function for search, or
        add to a file that will be read in the actual search function.

        :param uri: URI to connect to the database
        :param user: The username for connecting to the database
        :param password: The password that goes with the username
        """
        try:
            with GraphDatabase.driver(uri, auth=(user, password)) as driver:
                with driver.session(database="neo4j") as session:
                    session.execute_read(self._get_names)
        except ServiceUnavailable as exc:
            print("Restart the Neo4J database before running this code.")

    @abstractmethod
    def _get_names(self, tx) -> Iterable[str]:
        pass


class FulltextSearch(NameSearchNeo4J):
    def __init__(self, search_names: Optional[Iterable[str]] = None):
        super().__init__(search_names=search_names)
        self.query = (
            'CALL db.index.fulltext.queryNodes("Everything_Names", $name) '
            'YIELD node, score '
            'RETURN node.name, node.node_id, score'
        )

    def _get_names(self, tx) -> None:
        """
        The transactions to search the database are performed here and written to
        a csv file.

        :param tx: The database session to use for searching
        """
        with open(CONFIG["SEARCH_OUTPUT"], "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter="|", )
            csv_writer.writerow(LeakNode._fields)

            for name in self.search_names:
                results = tx.run(self.query, name=name)
                csv_writer.writerows(LeakNode(name, *result.values()) for result in results)


class FuzzyMatchSearch(NameSearchNeo4J):
    def __init__(self, search_names: Optional[Iterable[str]] = None):
        super().__init__(search_names=search_names)
        self.node_attrs = {"node.name", "node.original_name", "node.former_name", "node.company_name", "node.node_id"}
        self.query = (
            "MATCH (node) WHERE node.name IS NOT NULL "
            f"RETURN {', '.join(self.node_attrs)}"
        )
        self.found_names = defaultdict(set)

    def _get_names(self, tx) -> None:
        results = tx.run(self.query)
        for item in results:
            for attr in self.node_attrs:
                if attr != "node.node_id" and item[attr] is not None:
                    self.found_names[item[attr]].add(item["node.node_id"])

        with open(CONFIG["SEARCH_OUTPUT"], "a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter="|", )
            csv_writer.writerow(LeakNode._fields)

            for name in self.search_names:
                results = extract(name, self.found_names.keys(), scorer=token_set_ratio, score_cutoff=75, )
                csv_writer.writerows(results)


if __name__ == '__main__':
    FuzzyMatchSearch().get_names()
