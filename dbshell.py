#!/usr/bin/env python
"""
Simple SQLite Shell for db.sqlite3
"""

import sqlite3
import sys

def main():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        print("SQLite version:", sqlite3.version)
        print("Connected to db.sqlite3")
        print('Enter ".tables" to show tables, ".quit" to exit')
        
        while True:
            try:
                query = input("sqlite> ").strip()
                
                if not query:
                    continue
                
                if query == '.quit' or query == '.exit':
                    break
                
                if query == '.tables':
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                    tables = cursor.fetchall()
                    for table in tables:
                        print(table[0])
                    continue
                
                # Execute query
                cursor.execute(query)
                
                # If SELECT, show results
                if query.upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    if cursor.description:
                        # Print column names
                        cols = [desc[0] for desc in cursor.description]
                        print('|'.join(cols))
                        print('-' * (len('|'.join(cols))))
                    
                    for row in rows:
                        print('|'.join(str(x) if x is not None else 'NULL' for x in row))
                    
                    if rows:
                        print(f"\n{len(rows)} rows")
                else:
                    # For INSERT, UPDATE, DELETE
                    conn.commit()
                    print(f"{cursor.rowcount} rows affected")
            
            except KeyboardInterrupt:
                print("\nInterrupt")
            except sqlite3.Error as e:
                print(f"Error: {e}")
            except EOFError:
                break
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Cannot connect to database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
