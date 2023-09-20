import os.path
import sqlite3
import json
import sys


def parse_tagfile(location):
    c = None
    with open(location, 'r') as fd:
        content = fd.read()
        c = json.loads(content)
    return c


def sync_tags(db: sqlite3.Connection, tags: list):
    c = db.cursor()
    c.executemany(
        'REPLACE INTO TAGS (id, '
        'category, description, descriptioneng, parent, hidefromsuggestions, targets, thumbMime) '
        'VALUES (:id, :categoryName, :description, :descriptionEng, :parent, :hidefromsuggestions, :targets, :thumbMime)',
        tags)
    db.commit()


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
    tags_to_sync = []
    tag_names_to_sync = []
    related_tag_ids = []
    tag_weblinks = []
    # TODO: this could be further optimized to store languages, categories etc. as references to distinct tables,
    #  which would save some storage space.
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            tags = parse_tagfile(fl)
            for tag in tags:
                tag_to_add = {
                    'id': tag.get('id'),
                    'categoryName': tag.get('categoryName'),
                    'description': tag.get('description', None),
                    'descriptionEng': tag.get('descriptionEng', None),
                    'hidefromsuggestions': tag.get('hideFromSuggestions'),
                    'thumbMime': tag.get('thumbMime'),
                    'targets': tag.get('targets'),
                    'parent': None if tag['parent'] is None else tag['parent']['id']
                }
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

                for wl in tag.get('webLinks', []):
                    link_to_add = {
                        'tag_id': tag.get('id'),
                        'category': wl.get('category'),
                        'description': wl.get('description'),
                        'url': wl.get('url'),
                        'disabled': wl.get('disabled')
                    }
                    tag_weblinks += (link_to_add,)
                # TODO: remove
                handled_keys = ['id', 'categoryName', 'description', 'descriptionEng', 'parent', 'names',
                                'hideFromSuggestions', 'relatedTags', 'webLinks', 'thumbMime', 'targets']
                for key in tag.keys():
                    if key not in handled_keys:
                        print('unhandled key: ' + str(key) + ', value: ' + str(tag[key]))

                tags_to_sync += (tag_to_add,)
    sync_tags(db, tags_to_sync)
    sync_tag_names(db, tag_names_to_sync)
    sync_related_tags(db, related_tag_ids)
    sync_weblinks(db, tag_weblinks)