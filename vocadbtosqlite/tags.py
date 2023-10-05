import os.path
import sqlite3
import json
import vocadbtosqlite.weblinks
import vocadbtosqlite.names


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
                    tag_names_to_process += (tn,)

                # TODO: this could be optimized by checking if the relationship is already stored in reverse in DB
                for rt in tag.get('relatedTags', []):
                    related_tag_ids_to_process += ({'a': tag.get('id'), 'b': rt.get('id')},)

                for wl in tag.get('webLinks', []):
                    wl['tag_id'] = tag.get('id')
                    tag_weblinks_to_process += (wl,)

    sync_tags(db, tags_to_process)
    vocadbtosqlite.names.add_names(tag_names_to_process, c)
    vocadbtosqlite.names.batch_link_tag_names(tag_names_to_process, c)
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


def link_songs(entries: list, cursor: sqlite3.Cursor):
    for e in entries:
        try:
            cursor.execute('''
                INSERT INTO SONGS_TAGS (song_id, tag_id) VALUES (:song_id, :tag_id) ON CONFLICT DO NOTHING
                ''', e)
        except sqlite3.IntegrityError:
            # Ignore deleted tags
            pass


def link_artists(entries: list, cursor: sqlite3.Cursor):
    for e in entries:
        try:
            cursor.execute('''
                INSERT INTO ARTISTS_TAGS (artist_id, tag_id) VALUES (:artist_id, :tag_id) ON CONFLICT DO NOTHING
                ''', e)
        except sqlite3.IntegrityError:
            # Ignore deleted tags
            pass


def link_event_series(entries: list, cursor: sqlite3.Cursor):
    for e in entries:
        try:
            cursor.execute('''
                INSERT INTO EVENT_SERIES_TAGS (series_id, tag_id) VALUES (:series_id, :tag_id) ON CONFLICT DO NOTHING
                ''', e)
        except sqlite3.IntegrityError:
            # Ignore deleted tags
            pass


def link_events(entries: list, cursor: sqlite3.Cursor):
    for e in entries:
        try:
            cursor.execute('''
                INSERT INTO EVENTS_TAGS (event_id, tag_id) VALUES (:event_id, :tag_id) ON CONFLICT DO NOTHING
                ''', e)
        except sqlite3.IntegrityError:
            # Ignore deleted tags
            pass
