def all_events(cursor):
    cursor.execute('''
        SELECT  *
        FROM    events
        ''')
    columns = [column[0] for column in cursor.description]  # Get column names
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]  # Create list of dictionaries
