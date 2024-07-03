import sqlite3

DATABASE_NAME = 'branding_photos.db'

def create_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY,
            global_id TEXT,
            national_project TEXT,
            object_type TEXT,
            region TEXT,
            city TEXT,
            street TEXT,
            house TEXT,
            photo_url TEXT,
            errors TEXT,
            info TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_photo(global_id, national_project, object_type, region, city, street, house, photo_url, errors, info):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO photos(global_id, national_project, object_type, region, city, street, house, photo_url, errors, info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (global_id, national_project, object_type, region, city, street, house, photo_url, errors, info))
    conn.commit()
    conn.close()
