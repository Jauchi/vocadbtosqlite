import sqlite3


# Todo: move this from src to here

def link_albums(entries: [dict], cursor: sqlite3.Cursor):
    cursor.executemany('''
        INSERT INTO ALBUMS_PVS (album_id, pv_id, pv_service) VALUES (:album_id, :pvId, :service) 
        ON CONFLICT DO NOTHING
    ''', entries)


def link_songs(entries: [dict], cursor: sqlite3.Cursor):
    cursor.executemany('''
        INSERT INTO SONGS_PVS (song_id, pv_id, pv_service) VALUES (:song_id, :pvId, :service) 
        ON CONFLICT DO NOTHING
    ''', entries)


def add_pvs(pvs: [dict], cursor: sqlite3.Cursor):
    for i in pvs:
        if i.get('extendedMetadata', False):
            i['extendedMetadataStr'] = str(i['extendedMetadata'])
        else:
            i['extendedMetadataStr'] = None

    cursor.executemany('''
    INSERT INTO PVS (author, disabled, extendedMetadata, length, name, publishDate, pvId, service, pvType, thumbUrl)
    VALUES
    (:author, :disabled, :extendedMetadataStr, :length, :name, :publishDate, :pvId, :service, :pvType, :thumbUrl)
    ON CONFLICT DO NOTHING
    ''', pvs)