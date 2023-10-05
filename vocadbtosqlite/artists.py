import datetime
import sqlite3
import vocadbtosqlite.weblinks
import sqlite3
import os
import vocadbtosqlite.util


# TODO: make this prettier
def parse_artist_dir(db: sqlite3.Connection, location):
    i = 0
    all_artists = []

    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            # print('Processing: ' + str(fl))
            all_artists += vocadbtosqlite.util.parse_json(fl)

    add_artists(all_artists, cursor=db.cursor())
    db.commit()


def link_albums_artists(entries: [dict], c: sqlite3.Cursor):
    c.executemany('''
                INSERT INTO ALBUMS_ARTISTS (album_id, artist_id, is_support, roles)
                VALUES
                (:album_id, :id, :isSupport, :roles)
                ON CONFLICT DO NOTHING
            ''', entries)


def add_artists(artist_lst: list, cursor: sqlite3.Cursor):
    # TODO LATER: add artistType table (dedup)
    # TODO LATER: implement this strategy for the other data type (cannot remember rn)

    # TODO: groups, members, baseVoicebank, releaseDate, translatedName, webLinks
    # Initially, we leave baseVoicebank empty to avoid having to do recursion. We later update it.
    cursor.executemany('''
        INSERT INTO ARTISTS(
            artistType, description, descriptionEng, artist_id, mainPictureMime
        ) VALUES (:artistType, :description, :descriptionEng, :id, :mainPictureMime) ON CONFLICT DO NOTHING
    ''', artist_lst)

    # Gather more information:
    base_voicebanks = []
    artist_members = []
    weblinks = []

    for a in artist_lst:
        a_id = a.get('id')
        # Extract baseVoicebank
        if a.get('baseVoicebank') is not None:
            bvb = a.get("baseVoicebank")
            base_voicebanks += [(bvb['id'], a_id,)]
        # membership information
        if a.get('members'):
            for child in a.get('members'):
                artist_members += [(child['id'], a_id)]
        if a.get('groups'):
            for parent in a.get('groups'):
                artist_members += [(a_id, parent['id'],)]
        if a.get('webLinks'):
            for wl in a.get('webLinks'):
                wl['artist_id'] = a_id
                weblinks += (wl,)
    vocadbtosqlite.weblinks.add_artist_weblinks(weblinks, cursor)

    for member_pair in artist_members:
        try:
            cursor.execute('INSERT INTO ARTISTS_MEMBERS (parent_artist, child_artist) VALUES (?, ?) ON CONFLICT DO '
                           'NOTHING', member_pair)
        except sqlite3.IntegrityError:
            pass
    for bvb in base_voicebanks:
        try:
            cursor.execute('UPDATE ARTISTS SET baseVoicebank = ? where ARTISTS.artist_id = ?', bvb)
        except sqlite3.IntegrityError:
            # skip deleted objects...
            pass
