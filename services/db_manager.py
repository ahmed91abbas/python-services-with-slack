import sqlite3
from sqlite3 import Error

class Db_manager:

    def __init__(self, db_file, table_name):
        self.error_msg = None
        self.table_name = table_name
        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            self.error_msg = str(e)
            print(self.error_msg)
        return conn

    def select_all(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM {self.table_name}")
            rows = cur.fetchall()
        return rows

    def insert_values(self, cols, values):
        with self.conn:
            cur = self.conn.cursor()
            sql = f'''INSERT INTO {self.table_name}
                    ({",".join(cols)})
                    VALUES ({",".join(["?" for x in cols])})'''
            cur.execute(sql, (values))
        return cur.lastrowid

    def delete_where_condition(self, cols, values):
        where_stmt = self.create_where_statment(cols)
        try:
            cur = self.conn.cursor()
            sql = f'''DELETE FROM {self.table_name} {where_stmt}'''
            if not type(values) is list:
                list_values = [values]
            cur.execute(sql, (list_values))
            self.conn.commit()
            cur.close()
            if cur.rowcount:
                return values
        except Error as e:
            self.error_msg = str(e)
            print(str(e))
        return None

    def delete_all(self):
        sql = f'DELETE FROM {self.table_name}'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cur.close()
        return cur.rowcount

    def create_where_statment(self, cols):
        stmt = "WHERE "
        if type(cols) is list:
            stmt += " = ? AND ".join(cols) + " = ?"
        else:
            stmt += cols + " = ?"
        return stmt

