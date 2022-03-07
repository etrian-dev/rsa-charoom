# boilerplate copied from
# https://flask.palletsprojects.com/en/2.0.x/tutorial/database/

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    gdb = get_db().cursor()
    with current_app.open_resource('db_schema.sql') as f:
        gdb.executescript(f.read().decode('utf8'))
# TODO: untested
def querydb(query: str, args: list):
    '''Generator that queries the database and returns the resulting rows.
    '''
    cursor = get_db().execute(query, args)
    rows = cursor.fetchall()
    for row in rows:
        yield row

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
