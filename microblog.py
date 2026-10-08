import sqlalchemy as sql
from sqlalchemy import orm

from app import app, db
from app.models import Post, User


@app.shell_context_processor
def make_shell_context():
    return {'sql': sql, 'orm': orm, 'db': db, 'User': User, 'Post': Post}
