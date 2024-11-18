import sqlite3

from core.config import DBSQLiteSettings

_settings = DBSQLiteSettings()


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect(_settings.db_path)
        self.cursor = self.conn.cursor()

        self._check_db_exists()

    def insert(self, table, column_values):
        columns = ", ".join(column_values.keys())
        values = [tuple(column_values.values())]
        placeholders = ", ".join("?" * len(column_values.keys()))
        self.cursor.executemany(
            f"INSERT INTO {table} " f"({columns}) " f"VALUES ({placeholders})", values
        )
        self.conn.commit()

    def update(self, table, column_values, row_id): # TODO:check #18 `update` method on correct work 
        set_clause = ", ".join([f"{column} = ?" for column in column_values.keys()])
        values = list(column_values.values()) + [row_id]
        self.cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
        self.conn.commit()


    def fetchall(self, table, columns):
        columns_joined = ", ".join(columns)
        self.cursor.execute(f"SELECT {columns_joined} FROM {table}")
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            dict_row = {}
            for index, column in enumerate(columns):
                dict_row[column] = row[index]
            result.append(dict_row)
        return result

    def delete(self, table, row_id) -> None:
        row_id = int(row_id)
        self.cursor.execute(f"delete from {table} where id={row_id}")
        self.conn.commit()

    def get_cursor(self):  # TODO: #17 check `get_cursor` method on correct work
        return self.cursor

    def _init_db(self):
        with open(_settings.scaffold_sql, "r") as f:
            scaffold_sql = f.read()
        self.cursor.executescript(scaffold_sql)
        self.conn.commit()

    def _check_db_exists(self):
        self.cursor.execute(
            "SELECT name FROM sqlite_master " "WHERE type='table' AND name='config'"
        )
        table_exists = self.cursor.fetchall()
        if table_exists:
            return
        self._init_db()


database = DataBase()
