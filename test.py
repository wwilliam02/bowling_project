import sqlite3
from flask import g

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ---------------- QUERYING FUNCTIONS --------------

def query_db(query, args=(), one=False, commit=False):
    # if commit:
    #     db = get_db()
    #     cur = db.execute(query, args)
    #     db.commit()
    #     cur.close
    #     return None
    # cur = get_db().execute(query, args)
    # rv = cur.fetchall()
    # cur.close()
    # return (rv[0] if rv else None) if one else rv

    try:
            if commit:
                db = get_db()
                cur = db.execute(query, args)
                db.commit()
                cur.close()
                return None
            cur = get_db().execute(query, args)
            rv = cur.fetchall()
            cur.close()
            return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
            # Handle the error here
            print("SQLite error:", e)
            return e  # Or raise an exception if needed


# When teardown context we close the database.
def init_db(app):
    app.teardown_appcontext(close_db)
