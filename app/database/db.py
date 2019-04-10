"""
app.db.db
~~~~~~~~~~~

Functiond for setting up the database

"""

import click
from flask import current_app, g
from flask.cli import with_appcontext
import psycopg2
from instance.config import Config


def get_db():

    if 'db' not in g:
        g.db = psycopg2.connect(
                current_app.config['DATABASE']
                )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('database/schema.sql') as f:
        with db.cursor() as cursor:
            cursor.execute(f.read().decode('utf8'))

#: Database commands
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')

@click.command('dropall-db')
@with_appcontext
def dropall_db_command():
    """drop all tables."""
    db = get_db()
    with db:
        with db.cursor() as cursor:
            cursor.execute("""drop table users;""")
            cursor.execute("""drop table records;""")
            cursor.execute("""drop table blacklist;""")
        db.commit()
    click.echo('Dropped all tables')

@click.command('rollback-db')
@with_appcontext
def rollback_db_command():
    """Rollback previous transaction."""
    db = get_db()
    with db:
        with db.cursor() as cursor:
            cursor.execute("rollback;")
        db.commit()
    click.echo('Transaction rolled back')


# Register above commands with the application
def init_app(app):
    # call close_db when cleaning up after returning a response
    app.teardown_appcontext(close_db)
    # add a new command that can be called with flask command
    app.cli.add_command(init_db_command)
    app.cli.add_command(dropall_db_command)
    app.cli.add_command(rollback_db_command)
