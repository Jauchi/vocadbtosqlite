import sqlite3


# TODO: intersection table
def add_pvs(song_id: int, pv_list: list, cursor: sqlite3.Cursor):
    if pv_list:
        for i in pv_list:
            i['song_id'] = song_id
            if i['extendedMetadata']:
                i['extendedMetadataStr'] = str(i['extendedMetadata'])
            else:
                i['extendedMetadataStr'] = None
        cursor.executemany('''
        INSERT INTO PVS (author, disabled, extendedMetadata, length, name, publishDate, pvId, service, pvType, thumbUrl)
        VALUES
        (:author, :disabled, :extendedMetadataStr, :length, :name, :publishDate, :pvId, :service, :pvType, :thumbUrl)
        ON CONFLICT DO NOTHING
        ''', pv_list)
        cursor.executemany('''
            INSERT INTO SONGS_PVS (song_id, pvId, service) VALUES (:song_id, :pvId, :service) ON CONFLICT DO NOTHING
        ''', pv_list)
