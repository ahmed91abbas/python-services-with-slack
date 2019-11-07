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
        return conn

    def select_all(self):
        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute(f"SELECT * FROM {self.table_name}")
                rows = cur.fetchall()
            return rows
        except Error as e:
            self.error_msg = str(e)
        return None

    def select_where_condition(self, cond_kwargs, select_cols="*"):
        cols = list(cond_kwargs.keys())
        values = list(cond_kwargs.values())
        where_stmt = self.create_where_statment(cols)
        try:
            with self.conn:
                if type(select_cols) is list:
                    select_cols = ", ".join(select_cols)
                cur = self.conn.cursor()
                sql = f'''SELECT {select_cols} FROM {self.table_name} {where_stmt}'''
                cur.execute(sql, (values))
                return cur.fetchall()
        except Error as e:
            self.error_msg = str(e)
        return None

    def insert_values(self, cols, values):
        try:
            with self.conn:
                cur = self.conn.cursor()
                sql = f'''INSERT INTO {self.table_name}
                        ({",".join(cols)})
                        VALUES ({",".join(["?" for x in cols])})'''
                cur.execute(sql, (self.to_list(values)))
            return cur.lastrowid
        except Error as e:
            self.error_msg = str(e)
        return None

    def delete_where_condition(self, cols, values):
        where_stmt = self.create_where_statment(cols)
        try:
            cur = self.conn.cursor()
            sql = f'''DELETE FROM {self.table_name} {where_stmt}'''
            cur.execute(sql, (self.to_list(values)))
            self.conn.commit()
            cur.close()
            if cur.rowcount:
                return values
        except Error as e:
            self.error_msg = str(e)
        return None

    def delete_all(self):
        try:
            sql = f'DELETE FROM {self.table_name}'
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            return cur.rowcount
        except Error as e:
            self.error_msg = str(e)
        return None

    def create_where_statment(self, cols):
        stmt = "WHERE "
        if type(cols) is list:
            stmt += " = ? AND ".join(cols) + " = ?"
        else:
            stmt += cols + " = ?"
        return stmt

    def to_list(self, values):
        if not type(values) is list:
            list_values = [values]
        else:
            list_values = values
        return list_values


