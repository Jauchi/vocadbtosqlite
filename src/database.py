#!/bin/python3

import sqlite3


def dbinit(dblocation):
    db = sqlite3.connect(dblocation)
    db.row_factory = sqlite3.Row
    db.cursor().executescript('''
    BEGIN TRANSACTION;
    CREATE TABLE IF NOT EXISTS "RELATED_TAGS" (
        "a"	INTEGER NOT NULL,
        "b"	INTEGER NOT NULL,
        FOREIGN KEY("a") REFERENCES "TAGS"("id"),
        FOREIGN KEY("b") REFERENCES "TAGS"("id"),
        PRIMARY KEY("a","b")
    );
    CREATE TABLE IF NOT EXISTS "WEBLINKS" (
        "link_id"   INTEGER NOT NULL,
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
        "thumbMime" TEXT,
        "targets" INTEGER,
        "hidefromsuggestions"	INTEGER CHECK("hidefromsuggestions" IN (0, 1)),
        FOREIGN KEY("parent") REFERENCES "TAGS"("id"),
        PRIMARY KEY("id","category")
    );
    CREATE TABLE IF NOT EXISTS "TAG_CATEGORIES" (
        "id"	INTEGER NOT NULL,
        "name"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    CREATE TABLE IF NOT EXISTS "LANGUAGES" (
        "id"	INTEGER NOT NULL UNIQUE,
        "language"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("id")
    );
    COMMIT;
    ''')
    db.commit()
    return db
