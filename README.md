# VocaDBToSqlite
## What does this do?
Uses a dump obtained from VocaDB and turns it into an sqlite database. Dumps can be downloaded using the provided `download_dump.sh` script.
## Goals
* Provide an efficient data source for analysis and scraping.
* Small file size.

## Limitations
Currently, the database represents a single dump *as is*. Updating using a different dump will result in an inconsistent database.
If you wish to keep track of changes over time, you need a database for each point in time.

Also, certain features (deleted tags, drafts) of VocaDB cannot be represented and are REMOVED from the database.