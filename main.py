import os.path

import vocadbtosqlite.database
import vocadbtosqlite.tags
import vocadbtosqlite.songs
import vocadbtosqlite.albums
import vocadbtosqlite.artists
import sqlite3

# TODO: make configurable
OUTPUT_DIRECTORY = 'data'
db = vocadbtosqlite.database.db_init('voca.db')

print('Parsing tags...')
vocadbtosqlite.tags.parse_tag_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Tags')
print('Parsing songs...')
vocadbtosqlite.songs.parse_song_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Songs')
# TODO: Artists
vocadbtosqlite.artists.parse_artist_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Artists')
# TODO: Events
print('Parsing Albums...')
vocadbtosqlite.albums.parse_album_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Albums')
