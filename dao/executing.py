from event import Event

def create_events_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS events
                    (id INTEGER PRIMARY KEY, category TEXT, name TEXT, year INTEGER, description TEXT)''')



def insert_event(conn, event: Event):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (category, name, year, description)
        VALUES (?, ?, ?, ?)
        ''', (event.category, event.name, event.year, event.description))
    conn.commit()

def update_event(conn, event: Event):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE events
        SET description = ?
        WHERE name = ? AND year = ?
        ''', (event.description, event.name, event.year))
    conn.commit()