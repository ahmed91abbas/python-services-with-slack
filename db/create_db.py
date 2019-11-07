import sqlite3

conn = sqlite3.connect('services_db.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS prayer_times (
            [generated_id] INTEGER PRIMARY KEY,
            [country] text,
            [city] text,
            [mosque] text,
            [month] text,
            [day] text,
            [fajr] text,
            [sunrise] text,
            [dhuhr] text,
            [asr] text,
            [maghrib] text,
            [isha] text)
            ''')

c.execute('''CREATE TABLE IF NOT EXISTS todo_list (
            [generated_id] INTEGER PRIMARY KEY,
            [text] text,
            [created_datetime] text)
            ''')

c.execute('''CREATE TABLE IF NOT EXISTS reminders (
            [generated_id] INTEGER PRIMARY KEY,
            [text] text,
            [created_datetime] text,
            [scheduled_datetime] text)
            ''')

conn.commit()