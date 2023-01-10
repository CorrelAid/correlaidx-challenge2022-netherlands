# correlaidx-challenge2022-netherlands

### FullText Search in Neo4J
The code can run as a script, or be imported as a function. It should be run from the base directory 
and expects the `data/` directory to already exist. 

The `.env` file should be in the root directory and needs the following items set:
```dotenv
NEO4J_URI="bolt://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD=""
SEARCH_NAMES_FILE="data/search_names.txt"
SEARCH_OUTPUT_FULLTEXT="data/search_fulltext_output.csv"
```
I've left the least sensitive values in, so potentially this could be run with just a password added.

The list of names should include one item to search per line. Overly common words will inflate the 
result and can usually be left out. For example `Jacob` is very common in the database, but `MacAdam` 
is not. Searching for `Jacob MacAdam` returns a lot of uninteresting results and searching for `MacAdam`
gives better results.
