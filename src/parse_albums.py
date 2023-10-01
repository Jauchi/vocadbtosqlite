import sqlite3
import os
import src.util
import vocadbtosqlite.names
import vocadbtosqlite.pvs
import sys
import src.pv


def link_albums_songs(to_add: list, cursor: sqlite3.Cursor):
    cursor.executemany('''
            INSERT INTO ALBUMS_SONGS (album_id, song_id, discNumber, trackNumber) VALUES 
            (:album_id, :song_id, :discNumber, :trackNumber) ON CONFLICT DO NOTHING
        ''', to_add)


def add_albums(albums: list, cursor: sqlite3.Cursor):
    cursor.executemany('''
        INSERT INTO ALBUMS (id, description, descriptionEng, discType, mainPictureMime) VALUES 
        (:id, :description, :descriptionEng, :discType, :mainPictureMime) ON CONFLICT DO NOTHING
    ''', albums)

    names_to_add = []
    pvs = []
    albums_songs = []
    for a in albums:
        a_id = a.get('id')
        for name in a.get('names'):
            name['album_id'] = a_id
        names_to_add += a['names']

        for pv in a.get('pvs'):
            pv['album_id'] = a_id
            pvs += (pv,)

        for s in a.get('songs', []):
            s_id = s.get('id')
            if s_id != 0:
                albums_songs += ({
                                     'album_id': a_id,
                                     'song_id': s.get('id'),
                                     'discNumber': s.get('discNumber'),
                                     'trackNumber': s.get('trackNumber')
                                 },)

    vocadbtosqlite.names.add_names(names_to_add, cursor)
    vocadbtosqlite.names.batch_link_albums(names_to_add, cursor)

    vocadbtosqlite.pvs.add_pvs(pvs, cursor)
    vocadbtosqlite.pvs.link_albums(pvs, cursor)

    link_albums_songs(albums_songs, cursor)


# , 'artists': [{'isSupport': False, 'roles': 0, 'id': 14, 'nameHint': '鏡音リン'}, {'isSupport': False, 'roles': 0, 'id': 1, 'nameHint': '初音ミク'}, {'isSupport': False, 'roles': 0, 'id': 292, 'nameHint': '椎名もた'}, {'isSupport': True, 'roles': 0, 'id': 314, 'nameHint': '黒魔'}, {'isSupport': True, 'roles': 0, 'id': 2219, 'nameHint': 'とんかつ'}, {'isSupport': True, 'roles': 0, 'id': 2220, 'nameHint': '削除'}, {'isSupport': False, 'roles': 0, 'id': 11480, 'nameHint': 'meisa'}, {'isSupport': True, 'roles': 512, 'id': 2010, 'nameHint': '抱きしめたトゥナイト'}, {'isSupport': False, 'roles': 256, 'id': 0, 'nameHint': 'PONKATSU'}, {'isSupport': True, 'roles': 0, 'id': 10124, 'nameHint': '000'}, {'isSupport': True, 'roles': 0, 'id': 13553, 'nameHint': '古川本舗'}, {'isSupport': False, 'roles': 0, 'id': 78, 'nameHint': '初音ミク Append (Soft)'}, {'isSupport': False, 'roles': 0, 'id': 79, 'nameHint': '初音ミク Append (Sweet)'}],
# 'identifiers': [],
# 'originalRelease': {'catNum': 'SNMT-0005',
# 'releaseDate': {'day': 5, 'isEmpty': False, 'month': 2, 'year': 2012},
# 'pictures': None,
# 'translatedName': {'default': 'alpa', 'defaultLanguage': 'Japanese', 'english': 'alpa', 'japanese': 'alpa', 'romaji': 'alpa'},
# 'webLinks': [{'category': 'Reference', 'description': 'MikuWiki', 'disabled': False, 'url': 'http://www5.atwiki.jp/hmiku/pages/20918.html'}, {'category': 'Commercial', 'description': 'Amazon (JP)', 'disabled': False, 'url': 'http://www.amazon.co.jp/alpa-%E6%A4%8E%E5%90%8D%E3%82%82%E3%81%9F/dp/B007PDCP0S'}, {'category': 'Reference', 'description': 'Discogs', 'disabled': False, 'url': 'https://www.discogs.com/%E3%81%BD%E3%82%8F%E3%81%BD%E3%82%8FP-alpa/release/12161312'}, {'category': 'Reference', 'description': 'Vocaloid Wiki', 'disabled': False, 'url': 'https://vocaloid.fandom.com/wiki/Alpa'}, {'category': 'Commercial', 'description': 'Google Play', 'disabled': False, 'url': 'https://play.google.com/store/music/album?id=B7cpb6pej2v237g7hj2iulzn6ju'}, {'category': 'Commercial', 'description': 'iTunes (US)', 'disabled': False, 'url': 'https://music.apple.com/us/album/1501467122?mt=1&app=music'}, {'category': 'Commercial', 'description': 'Spotify', 'disabled': False, 'url': 'https://open.spotify.com/album/092T0Gh5nfZN3pwroc01AP'}, {'category': 'Commercial', 'description': 'Amazon (US)', 'disabled': False, 'url': 'https://www.amazon.com/gp/product/B085G1TKKK/'}]}
def parse_album_dir(db: sqlite3.Connection, location):
    all_albums = []
    c = db.cursor()
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            # print('Processing: ' + str(fl))
            albums = src.util.parse_json(fl)
            all_albums += albums

    add_albums(albums=all_albums, cursor=c)
    db.commit()
