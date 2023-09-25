import os.path
import sqlite3
import json
import sys

import src.parse_weblinks


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


# TODO: batch processing
def link_song_id_to_tag(song_id: int, tag_id: int, c: sqlite3.Cursor):
    try:
        c.execute('INSERT INTO SONGS_TAGS (song_id, tag_id) VALUES (:song_id, :tag_id) ON CONFLICT DO NOTHING', {
            'song_id': song_id,
            'tag_id': tag_id
        })
    except sqlite3.IntegrityError:
        # Deleted tags do not show up in tags JSON, but still in Songs JSON.
        pass


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
            print('Skipping nonexistant tag relationship - A: ' + str(t['a']) + ' B: ' + str(t['b']))
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
    src.parse_weblinks.link_tags_to_weblinks(weblink_list=tag_weblinks_to_process, cursor=c)
