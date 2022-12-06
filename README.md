# CorrelAidX Challenge 2022: Team Netherlands

## About

This is the repo for the team of the Netherlands CorrelAid chapter for the 2022 CorrelAidX Challenge.
The challenge is a collaboration with investigative journalists to discover interesting local stories 
in the massive offshore data leaks that have become available in the past ten years. 

## Set Up

To get set-up from a technical standpoint, you need access to the data and a way of processing it.

### Data Sources

The main data source we are using is the [ICIJ Offshore Leaks Database](https://offshoreleaks.icij.org/).
This can be searched in a basic way directly via browser from their website.
The data set can also be [downloaded](https://offshoreleaks.icij.org/pages/database) from there.
There is also a [GitHub repo](https://github.com/ICIJ/offshoreleaks-data-packages) available. 

The data set is a combination of [five major leaks](https://offshoreleaks.icij.org/pages/data).
These are the famous Panama, Paradise and Pandora Papers as well as Offshore Leaks and Bahamas Leaks.
Despite the intimidating size of these links, the data set is actually manageable at the individual machine level.
This is because we are working with a graph database showing the links between people and companies,
rather than working with all the underlying documents themselves.

From their website, the data is available as a zip file consisting of csv files for generic use.
Via the GitHub repo, the data is available as a Neo4j database dump file for direct usage with that software.

### Data Processing

Although it is possible to use the system of your choice to analyse the data, 
particularly when working with the csv download, our default solution will be Neo4j.
This an intuitive choice as it is system already being used by ICIJ.

An easy way to work with Neo4j is to [download Neo4j Desktop](https://neo4j.com/download/), 
which is free to use for small scale purposes like our own.
The readme of the repo shows you how to set up a database from the dump file, but misses out a crucial last step.
At the time of writing, the dump file uses the indexing structure of Neo4j version 4 rather than the current version 5.
So after following the steps, you do have to change the version to 4.X.XX before clicking create. 
Once created, clicking the open button launches the Neo4j browser where you can run Cypher queries.
For more intuitive searching/browsing, you can instead click the arrow on _Open_ and use Neo4j Bloom instead.

Using the csv downloads, you can work directly with your preferred data science frameworks.
However, it is also possible to use Neo4j via Python.
In the notebooks folder, you can find a notebook demonstrating how to make a connection to the database with Python.
Note again the need to have version 4 of the driver, i.e. installing a version 4 of the Neo4j python package.
