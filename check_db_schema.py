#!/usr/bin/env python3
import sqlite3
import os

db_path = 'obesity_tracker.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='predictions';")
    schema = cursor.fetchone()
    if schema:
        print('Table definition:')
        print(schema[0])
        print('\n' + '='*50 + '\n')
    
    # Get column info
    cursor.execute('PRAGMA table_info(predictions);')
    columns = cursor.fetchall()
    print('Column information:')
    for col in columns:
        print(f'  {col[1]} {col[2]} (nullable: {not col[3]})')
    
    conn.close()
else:
    print('Database file not found')