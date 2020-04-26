#!/usr/bin/python3 -u
# encoding: utf-8
import os.path
import sqlite3 as sql

# database info
_database = 'remote_movies.db'
_schema = 'schema.sql'
_table_name = 'remote_movies'

_db_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), _database))
_schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), _schema))


class FileTransferDB(object):
    def __init__(self,
                 db_path=_db_path,
                 schema_path=_schema_path,
                 table_name=_table_name):
        self.db_path = db_path
        self.schema_path = schema_path
        self.table_name = table_name
        self._create_from_schema()

    def _create_from_schema(self):
        connection = sql.connect(self.db_path)
        connection.row_factory = sql.Row
        cur = connection.cursor()
        with open(self.schema_path) as schema:
            cur.executescript(schema.read())

    def insert(self, guid, remote_path):
        statement = f"INSERT INTO {self.table_name} (guid, remote_path) " \
                    f"VALUES (?, ?)"
        params = (guid, remote_path)
        with sql.connect(self.db_path) as con:
            con.row_factory = sql.Row
            con.text_factory = lambda x: str(x, "utf-8", "ignore")
            cur = con.cursor()
            cur.execute(statement, params)
            con.commit()

    def _select_movie(self, query):
        query_sql = f"SELECT * FROM {self.table_name} WHERE {query}"
        with sql.connect(self.db_path) as con:
            con.row_factory = sql.Row
            con.text_factory = lambda x: str(x, "utf-8", "ignore")
            cur = con.cursor()
            cur.execute(query_sql)

            return cur

    def select_guid(self, guid):
        statement = f"SELECT * FROM {self.table_name} WHERE guid=?"
        params = (guid,)
        with sql.connect(self.db_path) as con:
            con.row_factory = sql.Row
            con.text_factory = lambda x: str(x, "utf-8", "ignore")
            cur = con.cursor()
            cur.execute(statement, params)
            result = cur.fetchone()

        return result

    def select_all_movies(self):
        query_sql = f"SELECT * FROM {self.table_name}"
        with sql.connect(self.db_path) as con:
            con.row_factory = sql.Row
            con.text_factory = lambda x: str(x, "utf-8", "ignore")
            cur = con.cursor()
            cur.execute(query_sql)
            rows = cur.fetchall()

        return rows

    def select_all_unqueued_movies(self):
        unqueued_query = "queued = 0 AND complete = 0"
        cur = self._select_movie(unqueued_query)
        rows = cur.fetchall()

        return rows

    def select_all_queued_incomplete(self):
        incomplete_query = "queued = 1 AND complete = 0"
        cur = self._select_movie(incomplete_query)
        rows = cur.fetchall()

        return rows

    def select_one_incomplete(self):
        incomplete_query = "queued = 1 AND complete = 0"
        cur = self._select_movie(incomplete_query)
        result = cur.fetchone()

        return result

    def _update_status(self, guid, column, val):
        statement = f"UPDATE {self.table_name} SET {column} = {val} " \
                    f"WHERE guid=?"
        params = (guid,)
        with sql.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(statement, params)
            con.commit()

    def mark_queued(self, guid):
        self._update_status(guid, "queued", 1)
        self._update_status(guid, "complete", 0)

    def mark_complete(self, guid):
        self._update_status(guid, "queued", 0)
        self._update_status(guid, "complete", 1)

    def mark_unqueued_incomplete(self, guid):
        self._update_status(guid, "queued", 0)
        self._update_status(guid, "complete", 0)

    def remove_guid(self, guid):
        statement = f"DELETE FROM {self.table_name} WHERE guid=?"
        params = (guid,)
        with sql.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(statement, params)

    @staticmethod
    def row_to_dict(row):
        return dict(list(zip(list(row.keys()), row)))
