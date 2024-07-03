import sqlite3

DATABASE_NAME = 'branding_photos.db'

def create_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            global_id TEXT,
            national_project TEXT,
            object_type TEXT,
            region TEXT,
            city TEXT,
            street TEXT,
            house TEXT,
            photo_url TEXT,
            detected_errors TEXT,
            ocr_class TEXT,
            color_class TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_photo(global_id, national_project, object_type, region, city, street, house, photo_url, detected_errors, ocr_class, color_class):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO photos (global_id, national_project, object_type, region, city, street, house, photo_url, detected_errors, ocr_class, color_class)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (global_id, national_project, object_type, region, city, street, house, photo_url, detected_errors, ocr_class, color_class))
    conn.commit()
    conn.close()
