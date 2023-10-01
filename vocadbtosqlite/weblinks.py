import sqlite3


def __add_wl(wl_dict: dict, c: sqlite3.Cursor):
    c.execute('INSERT INTO WEBLINKS (category, description, disabled, url) VALUES '
              '(:category, :description, :disabled, :url) ON CONFLICT DO NOTHING', wl_dict)


def __add_wls(wl_list: [dict], c: sqlite3.Cursor):
    c.executemany("INSERT INTO WEBLINKS (category, description, disabled, url) VALUES "
                  "(:category, :description, :disabled, :url) ON CONFLICT DO NOTHING", wl_list)


def add_artist_weblinks(wl_list: [dict], c: sqlite3.Cursor):
    __add_wls(wl_list, c)
    c.executemany('INSERT INTO ARTISTS_WEBLINKS VALUES (:artist_id, (SELECT link_id FROM WEBLINKS WHERE '
                  'WEBLINKS.category = :category AND '
                  'WEBLINKS.description = :description AND '
                  'WEBLINKS.url = :url)) ON CONFLICT DO NOTHING',
                  wl_list)


# Will add weblinks
# Additionally lets you specify song_id, tag_id, album_id as a dictionary key.
# These will then be linked.
def link_to_weblinks(weblink_list, cursor: sqlite3.Cursor):
    __add_wls(weblink_list, cursor)
    tag_links = []
    song_links = []
    album_links = []
    for wl in weblink_list:
        if 'tag_id' in wl:
            tag_links += (wl,)
        if 'song_id' in wl:
            song_links += (wl,)
        if 'album_id' in wl:
            album_links += (wl,)
    if len(tag_links) > 0:
        cursor.executemany('INSERT INTO TAGS_WEBLINKS VALUES (:tag_id, (SELECT link_id FROM WEBLINKS WHERE '
                           'WEBLINKS.category = :category AND '
                           'WEBLINKS.description = :description AND '
                           'WEBLINKS.url = :url)) ON CONFLICT DO NOTHING',
                           tag_links)
    if len(song_links) > 0:
        cursor.executemany('INSERT INTO SONGS_WEBLINKS VALUES (:song_id, (SELECT link_id FROM WEBLINKS WHERE '
                           'WEBLINKS.category = :category AND '
                           'WEBLINKS.description = :description AND '
                           'WEBLINKS.url = :url)) ON CONFLICT DO NOTHING',
                           song_links)
    if len(album_links) > 0:
        cursor.executemany('INSERT INTO ALBUMS_WEBLINKS VALUES (:album_id, (SELECT link_id FROM WEBLINKS WHERE '
                           'WEBLINKS.category = :category AND '
                           'WEBLINKS.description = :description AND '
                           'WEBLINKS.url = :url)) ON CONFLICT DO NOTHING',
                           album_links)
