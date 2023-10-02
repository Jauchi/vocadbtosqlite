import os.path
import sqlite3
import json
import vocadbtosqlite.weblinks


def parse_tagfile(location):
    c = None
    with open(location, 'r') as fd:
        content = fd.read()
        c = json.loads(content)
    return c


def sync_tags(db: sqlite3.Connection, tags: list):
    c = db.cursor()

    while len(tags) > 0:
        tag = tags.pop(0)
        try:
            c.execute('INSERT INTO TAGS (id, '
                      'category, description, descriptioneng, parent, hidefromsuggestions, targets, thumbMime) '
                      'VALUES (:id, :categoryName, :description, :descriptionEng, :parent_id, :hideFromSuggestions, '
                      ':targets,'
                      ':thumbMime) ON CONFLICT DO NOTHING', tag)
        except sqlite3.IntegrityError:
            # Not all requirements (parent) were added yet, put the tag at the end of the list and try again later...
            tags.append(tag)

    db.commit()


def sync_tag_names(db: sqlite3.Connection, names: list):
    c = db.cursor()
    c.executemany('INSERT INTO TAG_NAMES (tag_id, language, value) VALUES (:tag_id, :language, :value) ON CONFLICT '
                  'DO NOTHING', names)
    db.commit()


def sync_related_tags(db: sqlite3.Connection, related_tags: list):
    c = db.cursor()
    # TODO: We get inconsistent data from the dump sometimes, so... just ignore it, I guess?
    for t in related_tags:
        try:
            c.execute('INSERT INTO RELATED_TAGS (a,b) VALUES (:a, :b) ON CONFLICT DO NOTHING', t)
        except sqlite3.IntegrityError:
            # Skip deleted tags.
            pass
    db.commit()


def sync_weblinks(db: sqlite3.Connection, tag_weblinks: list):
    c = db.cursor()
    c.executemany('INSERT INTO TAG_WEBLINKS (tag_id, category, description, url, disabled) VALUES '
                  '(:tag_id, :category, :description, :url, :disabled) ON CONFLICT DO NOTHING', tag_weblinks)
    db.commit()


def parse_tag_dir(db: sqlite3.Connection, location):
    c = db.cursor()
    # TODO: this could be further optimized to store languages, categories etc. as references to distinct tables,
    #  which would save some storage space.

    # This will read ALL information into memory and dump it later.
    # Currently, this is the best way to deal with foreign key constraints.
    # Pull-Requests welcome, of course!

    tags_to_process = []
    tag_names_to_process = []
    related_tag_ids_to_process = []
    tag_weblinks_to_process = []
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            tags = parse_tagfile(fl)

            for tag in tags:
                # parent is a dict, so we extract the ID for sqlite:
                tag['parent_id'] = None if not tag['parent'] else tag['parent']['id']
                tags_to_process += (tag,)

                tag_names = tag.get('names', [])
                for tn in tag_names:
                    tn['tag_id'] = tag.get('id')
                tag_names_to_process += tag_names

                # TODO: this could be optimized by checking if the relationship is already stored in reverse in DB
                for rt in tag.get('relatedTags', []):
                    related_tag_ids_to_process += ({'a': tag.get('id'), 'b': rt.get('id')},)

                for wl in tag.get('webLinks', []):
                    wl['tag_id'] = tag.get('id')
                    tag_weblinks_to_process += (wl,)

    sync_tags(db, tags_to_process)
    sync_tag_names(db, tag_names_to_process)
    sync_related_tags(db, related_tag_ids_to_process)
    vocadbtosqlite.weblinks.link_to_weblinks(weblink_list=tag_weblinks_to_process, cursor=c)


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
