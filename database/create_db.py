import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('../posts_database.db')  # Creates a SQLite database in memory
        return conn
    except Error as e:
        print(e)

    return conn

def create_user_table(conn):
    try:
        query = '''CREATE TABLE User (
                        id integer PRIMARY KEY,
                        username text NOT NULL,
                        profile_url text,
                        created_at text
                    );'''

        conn.execute(query)
    except Error as e:
        print(e)

def create_post_table(conn):
    try:
        query = '''CREATE TABLE Post (
                        id integer PRIMARY KEY,
                        pk_id integer,
                        user_id integer,
                        post_name string,
                        post_text text,
                        post_url text,
                        posted_at text,
                        scraped_at text,
                        creator_id integer,
                        lang text,
                        possibly_sensitive boolean,
                        FOREIGN KEY (creator_id) REFERENCES User (id)
                    );'''

        conn.execute(query)
    except Error as e:
        print(e)

def create_interpretation_table(conn):
    try:
        query = '''CREATE TABLE Interpretation (
                        id integer PRIMARY KEY,
                        pk_id integer,
                        interpretation text,
                        interpreted_at text,
                        score integer,
                        model_id text,
                        FOREIGN KEY (pk_id) REFERENCES Post (pk_id)
                    );'''

        conn.execute(query)
    except Error as e:
        print(e)

def main():
    conn = create_connection()

    if conn is not None:
        create_user_table(conn)
        create_post_table(conn)
        create_interpretation_table(conn)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()