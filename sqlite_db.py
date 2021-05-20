import sqlite3

class DBHelper:

    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_regions(self):
        return self.cursor.execute('select * from regions order by id').fetchall()

    def get_region_eng(self, region_id):
        return self.cursor.execute('select id, name, name_eng from regions where id=?', (region_id,)).fetchone()

