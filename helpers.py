import sqlite3

def create_db():
    '''Creation of database'''
    
    # Create database, if one does not currently exist
    with sqlite3.connect('database.sqlite') as conn:
        c = conn.cursor()

        # Create users table
        c.execute(
            '''
                CREATE TABLE IF NOT EXISTS users (
                    id 'INTEGER' PRIMARY KEY, 
                    username 'TEXT', 
                    password 'TEXT'
                )
            '''
        )
        # Create events table
        c.execute(
            '''
                CREATE TABLE IF NOT EXISTS events (
                    id 'INTEGER' PRIMARY KEY,
                    name 'TEXT',
                    date 'DATE',
                    description 'TEXT',
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            '''
        )
        # Create rsvps table
        c.execute(
            '''
                CREATE TABLE IF NOT EXISTS rsvps (
                    user_id INTEGER,
                    event_id INTEGER,
                    PRIMARY KEY (user_id, event_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (event_id) REFERENCES events(id)
                )
            '''
        )
        # Create comments table
        c.execute(
            '''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    event_id INTEGER,
                    comment TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (event_id) REFERENCES events(id)
                )
            '''
        )

        conn.commit()