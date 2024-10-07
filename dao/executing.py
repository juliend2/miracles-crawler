from event import Event

def maybe_create_events_table(cursor):
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            category TEXT,
            name TEXT,
            year INTEGER,
            description TEXT,
            wikipedia_section_title TEXT
        )''')

def insert_event(conn, event: Event):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (category, name, year, description, wikipedia_section_title)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            event.category,
            event.name,
            event.year,
            event.description,
            ''
        )
    )
    conn.commit()

def update_event(conn, event: Event):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE events
        SET description = ?
        WHERE name = ? AND year = ?
        ''', (event.description, event.name, event.year))
    conn.commit()



def maybe_create_marys_requests_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marys_requests (
            id INTEGER PRIMARY KEY,
            event_id INTEGER,
            request TEXT
        )
        '''
    )

def insert_marys_request(conn, event_id: int, request: str):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO marys_requests
            (event_id, request)
        VALUES
            (?, ?)
        ''', (event_id, request))
    conn.commit()
