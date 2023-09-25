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
    c.executemany(
        'INSERT INTO TAGS (id, '
        'category, description, descriptioneng, parent, hidefromsuggestions, targets, thumbMime) '
        'VALUES (:id, :categoryName, :description, :descriptionEng, :parent_id, :hideFromSuggestions, :targets, '
        ':thumbMime) ON CONFLICT DO NOTHING',
        tags)
    db.commit()


# TODO: multi
def link_song_id_to_tag(song_id: int, tag_id: int, c: sqlite3.Cursor):
    c.execute('INSERT INTO SONGS_TAGS (song_id, tag_id) VALUES (:song_id, :tag_id) ON CONFLICT DO NOTHING', {
        'song_id': song_id,
        'tag_id': tag_id
    })


def sync_tag_names(db: sqlite3.Connection, names: list):
    c = db.cursor()
    c.executemany('REPLACE INTO TAG_NAMES (tag_id, language, value) VALUES (:tag_id, :language, :value)', names)
    db.commit()


def sync_related_tags(db: sqlite3.Connection, related_tags: list):
    c = db.cursor()
    c.executemany('REPLACE INTO RELATED_TAGS (a,b) VALUES (:a, :b)', related_tags)
    db.commit()


def sync_weblinks(db: sqlite3.Connection, tag_weblinks: list):
    c = db.cursor()
    c.executemany('REPLACE INTO TAG_WEBLINKS (tag_id, category, description, url, disabled) VALUES '
                  '(:tag_id, :category, :description, :url, :disabled)', tag_weblinks)
    db.commit()


def parse_tag_dir(db: sqlite3.Connection, location):
    c = db.cursor()
    tags_to_sync = []
    tag_names_to_sync = []
    related_tag_ids = []
    # TODO: this could be further optimized to store languages, categories etc. as references to distinct tables,
    #  which would save some storage space.
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            tags = parse_tagfile(fl)
            for tag in tags:
                if tag['parent'] is None:
                    tag['parent_id'] = None
                else:
                    tag['parent_id'] = tag['parent']['id']
                tags_to_sync += (tag,)

                for tn in tag.get('names', []):
                    to_add = {
                        'tag_id': tag.get('id'),
                        'language': tn.get('language', None),
                        'value': tn.get('value', None),
                        'translated': 0
                    }
                    tag_names_to_sync += (to_add,)

                # TODO: make this unique
                for rt in tag.get('relatedTags', []):
                    related_tag_ids += ({'a': tag.get('id'), 'b': rt.get('id')},)

                src.parse_weblinks.link_tags_to_weblinks(tag_id=tag.get('id'), weblink_list=tag.get('webLinks', []),
                                                         cursor=c)
                # TODO: remove
                # handled_keys = ['id', 'categoryName', 'description', 'descriptionEng', 'parent', 'names',
                #                 'hideFromSuggestions', 'relatedTags', 'webLinks', 'thumbMime', 'targets']
                # for key in tag.keys():
                #     if key not in handled_keys:
                #         print('unhandled key: ' + str(key) + ', value: ' + str(tag[key]))

    sync_tags(db, tags_to_sync)
    sync_tag_names(db, tag_names_to_sync)
    sync_related_tags(db, related_tag_ids)

