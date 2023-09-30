#!/bin/python3

import sqlite3

# TODO: LANGUAGE needs it's own table
def dbinit(db_location: str):
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
        FOREIGN KEY("a") REFERENCES "TAGS"("id"),
        FOREIGN KEY("b") REFERENCES "TAGS"("id"),
        PRIMARY KEY("a","b")
    );
    CREATE TABLE IF NOT EXISTS "WEBLINKS" (
        "link_id"	INTEGER NOT NULL,
        "category"	TEXT NOT NULL,
        "description"	TEXT,
        "disabled"	INTEGER,
        "url"	TEXT NOT NULL,
        UNIQUE("category", "description", "url"),
        PRIMARY KEY("link_id")
    );
    CREATE INDEX IF NOT EXISTS "WEBLINK_IDX"  ON "WEBLINKS" (
    "category",
    "description",
    "disabled",
    "url"
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
        PRIMARY KEY("tag_id","song_id"),
        FOREIGN KEY("tag_id") REFERENCES "TAGS"("id")
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
        "pvId"	TEXT NOT NULL,
        "service" TEXT NOT NULL,
        UNIQUE("song_id", "pvId", "service"),
        PRIMARY KEY("song_id", "pvId", "service"),
        FOREIGN KEY("song_id") REFERENCES "SONGS"("id"),
        FOREIGN KEY("pvId", "service") REFERENCES "PVS"("pvId", "service")
    );
    CREATE TABLE IF NOT EXISTS "TAG_CATEGORIES" (
        "id"	INTEGER NOT NULL,
        "name"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    
    CREATE UNIQUE INDEX IF NOT EXISTS "WEBLINKS_U_IDX" ON "WEBLINKS" (
        "category",
        "description",
        "disabled",
        "url"
    );
    
    CREATE UNIQUE INDEX IF NOT EXISTS "WEBLINKS_U_ID" ON "WEBLINKS" (
        "link_id"
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "TAG_ALT_IDX" ON "RELATED_TAGS" (
        "a",
        "b"
    );

    COMMIT;
    PRAGMA foreign_keys = ON;
    ''')
    db.commit()
    return db
