import sqlite3
import sys
import os
import src.util

import vocadbtosqlite.artists


# TODO: make this prettier
def parse_artist_dir(db: sqlite3.Connection, location):
    i = 0
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            # print('Processing: ' + str(fl))
            artists = src.util.parse_json(fl)
            vocadbtosqlite.artists.add_artists(artists, cursor=db.cursor())
            db.commit()

