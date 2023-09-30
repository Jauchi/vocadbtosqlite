# VocaDBToSqlite
## What does this do?
Uses a dump obtained from VocaDB and turns it into an sqlite database. Dumps can be downloaded using the provided `download_dump.sh` script.
## Goals
This project aims to provide a data source for analysis and scraping.

The database is much smaller than the extracted contents of the file, and can be zipped (and indices dropped) to achieve the smallest possible size.

It can also be used to provide a much more convenient access for data analysis purposes.

