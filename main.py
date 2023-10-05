import os.path

import vocadbtosqlite.database
import vocadbtosqlite.tags
import vocadbtosqlite.songs
import vocadbtosqlite.albums
import vocadbtosqlite.artists
import vocadbtosqlite.events
import vocadbtosqlite.eventseries

# TODO: make configurable
OUTPUT_DIRECTORY = 'data'
db = vocadbtosqlite.database.db_init('voca.db')

print('Parsing tags...')
vocadbtosqlite.tags.parse_tag_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Tags')
print('Parsing songs...')
vocadbtosqlite.songs.parse_song_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Songs')
print('Parsing artists...')
vocadbtosqlite.artists.parse_artist_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Artists')
print('Parsing EventSeries...')
vocadbtosqlite.eventseries.parse_event_series_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'EventSeries')
print('Parsing Events...')
vocadbtosqlite.events.parse_event_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Events')
print('Parsing Albums...')
vocadbtosqlite.albums.parse_album_dir(db, OUTPUT_DIRECTORY + os.path.sep + 'Albums')
