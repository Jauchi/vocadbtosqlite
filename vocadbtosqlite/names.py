import sqlite3


def add_names(names: list, cursor: sqlite3.Cursor):
    cursor.executemany('''
        INSERT INTO NAMES (language, value) VALUES (:language, :value) ON CONFLICT DO NOTHING
    ''', names)


def batch_link_songs(entries: list, cursor: sqlite3.Cursor):
    cursor.executemany('''
    INSERT INTO SONGS_NAMES (song_id, name_id) 
        VALUES (
        :song_id, 
        (SELECT name_id FROM NAMES where language = :language AND value = :value))
        ON CONFLICT DO NOTHING
    ''', entries)


def batch_link_albums(entries: list, cursor: sqlite3.Cursor):
    cursor.executemany('''
    INSERT INTO ALBUMS_NAMES (album_id, name_id) 
        VALUES (
        :album_id, 
        (SELECT name_id FROM NAMES where language = :language AND value = :value))
        ON CONFLICT DO NOTHING
    ''', entries)


def batch_link_artists(entries: [dict], cursor: sqlite3.Cursor):
    cursor.executemany('''
    INSERT INTO ARTISTS_NAMES (artist_id, name_id) 
        VALUES (
        :artist_id, 
        (SELECT name_id FROM NAMES where language = :language AND value = :value))
        ON CONFLICT DO NOTHING
    ''', entries)


def batch_link_tag_names(entries: [dict], cursor: sqlite3.Cursor):
    cursor.executemany('''
    INSERT INTO TAGS_NAMES (tag_id, name_id) 
        VALUES (
        :tag_id, 
        (SELECT name_id FROM NAMES where language = :language AND value = :value))
        ON CONFLICT DO NOTHING
    ''', entries)


def batch_link_event_series(entries: [dict], cursor: sqlite3.Cursor):
    cursor.executemany('''
    INSERT INTO EVENT_SERIES_NAMES (series_id, name_id) 
        VALUES (
        :series_id, 
        (SELECT name_id FROM NAMES where language = :language AND value = :value))
        ON CONFLICT DO NOTHING
    ''', entries)


def batch_link_events(entries: [dict], cursor: sqlite3.Cursor):
    cursor.executemany('''
    INSERT INTO EVENTS_NAMES (event_id, name_id) 
        VALUES (
        :event_id, 
        (SELECT name_id FROM NAMES where language = :language AND value = :value))
        ON CONFLICT DO NOTHING
    ''', entries)


# Links your object to a name.
# TODO: not effective for a lot of inserts...
def link(language: str, value: str, cursor: sqlite3.Cursor, song_id: int = None, tag_id: int = None):
    if song_id:
        table_name = 'SONG_NAMES'
        attribute_name = 'song_id'
        ext_value = song_id
    elif tag_id:
        table_name = 'TAG_NAMES'
        attribute_name = 'tag_id'
        ext_value = tag_id
    else:
        raise ValueError('You need to provide an ID to link a tag to!')
    cursor.execute(
        'INSERT INTO ' + str(table_name) + ' (' + attribute_name + ', name_id) VALUES (:ext_value, (SELECT name_id '
                                                                   'FROM NAMES where language = :language AND '
                                                                   'value = :value))'
                                                                   'ON CONFLICT DO NOTHING',
        {'ext_value': ext_value, 'language': language, 'value': value})
