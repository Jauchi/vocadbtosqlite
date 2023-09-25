import sqlite3


# TODO: add batch processing
def __add_wl(wl_dict: dict, c: sqlite3.Cursor):
    c.execute('INSERT INTO WEBLINKS (category, description, disabled, url) VALUES '
              '(:category, :description, :disabled, :url) ON CONFLICT DO NOTHING', wl_dict)


# TODO: add batch processing
def link_song_to_weblinks(song_id, weblink_list, db: sqlite3.Connection):
    c = db.cursor()
    for le in weblink_list:
        if le != {}:
            __add_wl(le, c)
            c.execute('INSERT OR IGNORE INTO SONGS_WEBLINKS VALUES (:song_id, (SELECT link_id FROM WEBLINKS WHERE '
                      'WEBLINKS.category = :category AND '
                      'WEBLINKS.description = :description AND '
                      'WEBLINKS.disabled = :disabled AND '
                      'WEBLINKS.url = :url))',
                      {'song_id': song_id,
                       'category': le.get('category'),
                       'description': le.get('description'),
                       'disabled': le.get('disabled'),
                       'url': le.get('url')
                       })


def link_tags_to_weblinks(tag_id, weblink_list, cursor: sqlite3.Cursor):
    for le in weblink_list:
        if le != {}:
            __add_wl(le, cursor)
            cursor.execute('INSERT INTO TAGS_WEBLINKS VALUES (:tag_id, (SELECT link_id FROM WEBLINKS WHERE '
                           'WEBLINKS.category = :category AND '
                           'WEBLINKS.description = :description AND '
                           'WEBLINKS.disabled = :disabled AND '
                           'WEBLINKS.url = :url)) ON CONFLICT DO NOTHING',
                           {'tag_id': tag_id,
                            'category': le.get('category'),
                            'description': le.get('description'),
                            'disabled': le.get('disabled'),
                            'url': le.get('url')
                            })
