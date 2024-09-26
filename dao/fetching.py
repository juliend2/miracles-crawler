def all_events(cursor):
    cursor.execute('''
        SELECT  *
        FROM    events
        ''')
    columns = [column[0] for column in cursor.description]  # Get column names
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]  # Create list of dictionaries


def all_events_without_marys_demands(cursor):
    cursor.execute('''
        SELECT      e.*
        FROM        events AS e
        LEFT JOIN   marys_requests AS mr ON mr.event_id = e.id 
        WHERE       mr.id IS NULL
        ''')
    columns = [column[0] for column in cursor.description]  # Get column names
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]  # Create list of dictionaries