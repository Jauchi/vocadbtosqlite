import os.path

import src.database
import src.parse_tags
import sqlite3

# TODO: make configurable
OUTPUT_DIRECTORY = 'data'
db = src.database.dbinit('voca.db')

print('Parsing tags...')
src.parse_tags.parse_tag_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Tags')
