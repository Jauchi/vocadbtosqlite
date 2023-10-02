#!/bin/python3
import sqlite3


# TODO: LANGUAGE needs it's own table
def db_init(db_location: str):
    db = sqlite3.connect(db_location)
    db.row_factory = sqlite3.Row
    db.cursor().executescript('''
    BEGIN TRANSACTION;
    CREATE TABLE IF NOT EXISTS "ALBUMS" (
        "id"	INTEGER NOT NULL,
        "description"	TEXT,
        "descriptionEng"	TEXT,
        "discType"	TEXT,
        "mainPictureMime"	TEXT,
        PRIMARY KEY("id")
    );
    CREATE TABLE IF NOT EXISTS "SONGS" (
        "id"	INTEGER NOT NULL,
        "lengthSeconds"	INTEGER,
        "nicoId"	TEXT,
        "notes"	TEXT,
        "notesEng"	TEXT,
        "publishDate"	TEXT,
        "songType"	TEXT,
        "maxMilliBpm"	INTEGER,
        "minMilliBpm"	INTEGER,
        PRIMARY KEY("id")
    );
    CREATE TABLE IF NOT EXISTS "RELATED_TAGS" (
        "a"	INTEGER NOT NULL,
        "b"	INTEGER NOT NULL,
        FOREIGN KEY("b") REFERENCES "TAGS"("id"),
        FOREIGN KEY("a") REFERENCES "TAGS"("id"),
        PRIMARY KEY("a","b")
    );
    CREATE TABLE IF NOT EXISTS "WEBLINKS" (
        "link_id"	INTEGER NOT NULL,
        "category"	TEXT NOT NULL,
        "description"	TEXT,
        "disabled"	INTEGER,
        "url"	TEXT NOT NULL,
        PRIMARY KEY("link_id"),
        UNIQUE("category","description","url")
    );
    CREATE TABLE IF NOT EXISTS "SONGS_WEBLINKS" (
        "song_id"	INTEGER NOT NULL,
        "weblink_id"	INTEGER NOT NULL,
        FOREIGN KEY("song_id") REFERENCES "SONGS"("id"),
        FOREIGN KEY("weblink_id") REFERENCES "WEBLINKS"("link_id"),
        UNIQUE("song_id","weblink_id")
    );
    CREATE TABLE IF NOT EXISTS "TAGS_WEBLINKS" (
        "tag_id"	INTEGER NOT NULL,
        "weblink_id"	INTEGER NOT NULL,
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id"),
        FOREIGN KEY("weblink_id") REFERENCES "WEBLINKS"("link_id"),
        UNIQUE("tag_id","weblink_id")
    );
    CREATE TABLE IF NOT EXISTS "TAG_NAMES" (
        "tag_id"	INTEGER,
        "language"	INTEGER,
        "value"	INTEGER,
        PRIMARY KEY("tag_id","language","value"),
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id")
    );
    CREATE TABLE IF NOT EXISTS "TAGS" (
        "id"	INTEGER NOT NULL UNIQUE,
        "category"	TEXT,
        "description"	TEXT,
        "descriptioneng"	TEXT,
        "parent"	INTEGER,
        "thumbMime"	TEXT,
        "targets"	INTEGER,
        "hidefromsuggestions"	INTEGER CHECK("hidefromsuggestions" IN (0, 1)),
        FOREIGN KEY("parent") REFERENCES "TAGS"("id"),
        PRIMARY KEY("id")
    );
    CREATE TABLE IF NOT EXISTS "SONGS_TAGS" (
        "song_id"	INTEGER NOT NULL,
        "tag_id"	INTEGER NOT NULL,
        FOREIGN KEY("song_id") REFERENCES "SONGS"("id"),
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id"),
        PRIMARY KEY("tag_id","song_id"),
        UNIQUE("song_id","tag_id")
    );
    CREATE TABLE IF NOT EXISTS "PVS" (
        "author"	TEXT,
        "disabled"	INTEGER,
        "extendedMetadata"	TEXT,
        "length"	INTEGER,
        "name"	TEXT,
        "publishDate"	TEXT,
        "pvId"	TEXT NOT NULL,
        "service"	TEXT NOT NULL,
        "pvType"	TEXT,
        "thumbUrl"	TEXT,
        PRIMARY KEY("pvId","service"),
        UNIQUE("pvId","service")
    );
    CREATE TABLE IF NOT EXISTS "SONGS_PVS" (
        "song_id"	INTEGER NOT NULL,
        "pv_id"	TEXT NOT NULL,
        "pv_service"	TEXT NOT NULL,
        FOREIGN KEY("song_id") REFERENCES "SONGS"("id"),
        PRIMARY KEY("song_id","pv_id","pv_service"),
        UNIQUE("song_id","pv_id","pv_service"),
        FOREIGN KEY("pv_id","pv_service") REFERENCES "PVS"("pvId","service")
    );
    CREATE TABLE IF NOT EXISTS "TAG_CATEGORIES" (
        "id"	INTEGER NOT NULL,
        "name"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    CREATE TABLE IF NOT EXISTS "ALBUM_TAGS" (
        "album_id"	INTEGER NOT NULL,
        "tag_id"	INTEGER NOT NULL,
        FOREIGN KEY("album_id") REFERENCES "ALBUMS"("id"),
        UNIQUE("album_id","tag_id"),
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id"),
        PRIMARY KEY("tag_id","album_id")
    );
    CREATE TABLE IF NOT EXISTS "NAMES" (
        "name_id"	INTEGER NOT NULL UNIQUE,
        "language"	INTEGER NOT NULL,
        "value"	TEXT NOT NULL,
        PRIMARY KEY("name_id")
    );
    CREATE TABLE IF NOT EXISTS "TAGS_NAMES" (
        "tag_id"	INTEGER NOT NULL,
        "name_id"	INTEGER NOT NULL,
        UNIQUE("name_id","tag_id"),
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id"),
        FOREIGN KEY("name_id") REFERENCES "NAMES"("name_id"),
        PRIMARY KEY("name_id","tag_id")
    );
    CREATE TABLE IF NOT EXISTS "ALBUMS_NAMES" (
        "album_id"	INTEGER NOT NULL,
        "name_id"	INTEGER NOT NULL,
        FOREIGN KEY("album_id") REFERENCES "ALBUMS"("id"),
        UNIQUE("album_id","name_id"),
        FOREIGN KEY("name_id") REFERENCES "NAMES"("name_id"),
        PRIMARY KEY("album_id","name_id")
    );
    CREATE TABLE IF NOT EXISTS "SONGS_NAMES" (
        "song_id"	INTEGER NOT NULL,
        "name_id"	INTEGER NOT NULL,
        PRIMARY KEY("name_id","song_id"),
        FOREIGN KEY("song_id") REFERENCES "SONGS"("id"),
        UNIQUE("song_id","name_id"),
        FOREIGN KEY("name_id") REFERENCES "NAMES"("name_id")
    );
    CREATE TABLE IF NOT EXISTS "ALBUMS_PVS" (
        "album_id"	INTEGER NOT NULL,
        "pv_id"	TEXT NOT NULL,
        "pv_service"	TEXT NOT NULL,
        FOREIGN KEY("album_id") REFERENCES "ALBUMS"("id"),
        FOREIGN KEY("pv_id","pv_service") REFERENCES "PVS"("pvId","service"),
        PRIMARY KEY("album_id","pv_id","pv_service")
    );
    CREATE TABLE IF NOT EXISTS "ALBUMS_SONGS" (
        "album_id"	INTEGER NOT NULL,
        "song_id"	INTEGER NOT NULL,
        "discNumber"	INTEGER NOT NULL,
        "trackNumber"	INTEGER NOT NULL,
        FOREIGN KEY("song_id") REFERENCES "SONGS"("id"),
        FOREIGN KEY("album_id") REFERENCES "ALBUMS"("id"),
        PRIMARY KEY("album_id","song_id")
    );
    CREATE TABLE IF NOT EXISTS "ALBUMS_TAGS" (
        "album_id"	INTEGER NOT NULL,
        "tag_id"	INTEGER NOT NULL,
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id"),
        FOREIGN KEY("album_id") REFERENCES "ALBUMS"("id"),
        PRIMARY KEY("album_id","tag_id")
    );
    CREATE TABLE IF NOT EXISTS "ARTISTS_NAMES" (
        "artist_id"	INTEGER NOT NULL,
        "name_id"	INTEGER NOT NULL,
        FOREIGN KEY("artist_id") REFERENCES "ARTISTS"("artist_id"),
        FOREIGN KEY("name_id") REFERENCES "NAMES"("name_id")
    );
    CREATE TABLE IF NOT EXISTS "ARTISTS_TAGS" (
        "artist_id"	INTEGER NOT NULL,
        "tag_id"	INTEGER NOT NULL,
        PRIMARY KEY("tag_id","artist_id"),
        FOREIGN KEY("artist_id") REFERENCES "ARTISTS"("artist_id"),
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id")
    );
    CREATE TABLE IF NOT EXISTS "ARTISTS_MEMBERS" (
        "parent_artist"	INTEGER NOT NULL,
        "child_artist"	INTEGER NOT NULL,
        PRIMARY KEY("parent_artist","child_artist"),
        UNIQUE("parent_artist","child_artist"),
        FOREIGN KEY("child_artist") REFERENCES "ARTISTS"("artist_id"),
        FOREIGN KEY("parent_artist") REFERENCES "ARTISTS"("artist_id")
    );
    CREATE TABLE IF NOT EXISTS "ARTISTS" (
        "artistType"	TEXT,
        "baseVoiceBank"	INTEGER,
        "description"	TEXT,
        "descriptionEng"	TEXT,
        "artist_id"	INTEGER NOT NULL UNIQUE,
        "mainPictureMime"	TEXT,
        "releaseDate"	TEXT,
        PRIMARY KEY("artist_id"),
        FOREIGN KEY("baseVoiceBank") REFERENCES "ARTISTS"("artist_id")
    );
    CREATE TABLE IF NOT EXISTS "ARTISTS_WEBLINKS" (
        "artist_id"	INTEGER NOT NULL,
        "weblink_id"	INTEGER NOT NULL,
        PRIMARY KEY("weblink_id","artist_id"),
        UNIQUE("artist_id","weblink_id"),
        FOREIGN KEY("weblink_id") REFERENCES "WEBLINKS"("link_id"),
        FOREIGN KEY("artist_id") REFERENCES "ARTISTS"("artist_id")
    );
    CREATE INDEX IF NOT EXISTS "WEBLINK_IDX" ON "WEBLINKS" (
        "category",
        "description",
        "disabled",
        "url"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "WEBLINKS_U_IDX" ON "WEBLINKS" (
        "category",
        "description",
        "url"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "WEBLINKS_U_ID" ON "WEBLINKS" (
        "link_id"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "TAG_ALT_IDX" ON "RELATED_TAGS" (
        "a",
        "b"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "SONG_IDX" ON "SONGS" (
        "id",
        "lengthSeconds",
        "nicoId",
        "notes",
        "notesEng",
        "publishDate",
        "songType",
        "maxMilliBpm",
        "minMilliBpm"
    );
    CREATE INDEX IF NOT EXISTS "ALBUM_NAMES_IDX" ON "ALBUMS_NAMES" (
        "album_id"
    );
    CREATE INDEX IF NOT EXISTS "SONG_NAMES_IDX" ON "SONGS_NAMES" (
        "song_id"
    );
    CREATE INDEX IF NOT EXISTS "NAME_IDX" ON "NAMES" (
        "language",
        "value"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "PV_U_IDX" ON "PVS" (
        "pvId",
        "service"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "ALBUM_PVS_IDX" ON "ALBUMS_PVS" (
        "album_id",
        "pv_id",
        "pv_service"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "ALBUMS_PVS_U_IDX" ON "ALBUMS_PVS" (
        "pv_id",
        "pv_service"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "ALBUMS_SONGS_U_PK" ON "ALBUMS_SONGS" (
        "album_id",
        "song_id"
    );
    CREATE INDEX IF NOT EXISTS "ALBUMS_TAGS_U_IDX" ON "ALBUMS_TAGS" (
        "album_id",
        "tag_id"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "ARTISTS_TAGS_U_IDX" ON "ARTISTS_TAGS" (
        "artist_id",
        "tag_id"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "ARTISTS_NAMES_U_IDX" ON "ARTISTS_NAMES" (
        "artist_id",
        "name_id"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "ARTISTS_U_IDX" ON "ARTISTS" (
        "artist_id"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "ARTISTS_WEBLINKS_U_IDX" ON "ARTISTS_WEBLINKS" (
        "artist_id",
        "weblink_id"
    );
    COMMIT;

    PRAGMA foreign_keys = ON;
    ''')
    db.commit()
    return db
