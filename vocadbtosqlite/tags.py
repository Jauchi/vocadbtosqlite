import sqlite3


def link_albums(entries: list, cursor: sqlite3.Cursor):
    for e in entries:
        try:
            cursor.execute('''
                INSERT INTO ALBUMS_TAGS (album_id, tag_id) VALUES (:album_id, :tag_id) ON CONFLICT DO NOTHING
                ''', e)
        except sqlite3.IntegrityError:
            # Ignore deleted tags
            pass


# Links your object to a tag. Can cause IntegrityErrors (i.e. will not check if the tag exists) which will need to be
# handled outside this function.
def link(tag_id: int, cursor: sqlite3.Cursor, song_id: int = None, album_id: int = None):
    if song_id:
        table_name = 'SONGS_TAGS'
        attribute_name = 'song_id'
        ext_value = song_id
    elif album_id:
        table_name = 'ALBUMS_SONGS'
        attribute_name = 'album_id'
        ext_value = album_id
    else:
        raise ValueError('You need to provide an ID to link a tag to!')
    cursor.execute(
        'INSERT INTO ' + str(table_name) + ' (' + attribute_name + ', tag_id) VALUES (:ext_value, :tag_id) '
                                                                   'ON CONFLICT DO NOTHING',
        {'ext_value': ext_value, 'tag_id': tag_id})
