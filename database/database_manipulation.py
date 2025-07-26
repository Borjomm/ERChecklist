import sqlite3
import json


def create_boss_database(processed_data, db_path='gamedata.db'):
    """
    Takes the final processed list of boss dictionaries and populates
    an SQLite database with it.
    """
    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Create the 'bosses' table ---
    # Using "IF NOT EXISTS" makes the script safely re-runnable.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bosses (
            boss_id             INTEGER PRIMARY KEY,
            name                TEXT NOT NULL,
            region              TEXT NOT NULL,
            is_remembrance      BOOLEAN NOT NULL,
            is_dlc              BOOLEAN NOT NULL,
            save_bit_offset     INTEGER NOT NULL UNIQUE,
            link                TEXT
        );
    ''')

    # --- Insert the data ---
    # Using executemany is much faster than inserting one row at a time.
    boss_tuples = [
        (
            boss['boss_id'],
            boss['name'],
            boss['region'],
            boss['is_remembrance'],
            boss['is_dlc'],
            boss['offset'],
            boss['link']
        )
        for boss in processed_data
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO bosses 
        (boss_id, name, region, is_remembrance, is_dlc, save_bit_offset, link) 
        VALUES (?, ?, ?, ?, ?, ?, ?);
    ''', boss_tuples)

    # --- Commit changes and close the connection ---
    conn.commit()
    conn.close()
    print(f"Successfully created and populated the bosses table in {db_path}")

if __name__ == "__main__":
    with open('database/final_bosses.json', 'r', encoding='utf-8') as f:
        final_boss_list = json.load(f)

    # 2. Call the function to build the database
    create_boss_database(final_boss_list)