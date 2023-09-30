import os.path

import src.database
import src.parse_tags
import src.parse_songs
import src.parse_albums
import sqlite3

# TODO: make configurable
OUTPUT_DIRECTORY = 'data'
db = src.database.dbinit('voca.db')

print('Parsing tags...')
src.parse_tags.parse_tag_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Tags')
print('Parsing songs...')
src.parse_songs.parse_song_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Songs')
# TODO: Artists
# TODO: Events
print('Parsing Albums...')
src.parse_albums.parse_album_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Albums')
