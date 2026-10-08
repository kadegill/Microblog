from datetime import datetime, timezone

import sqlalchemy as sql
from sqlalchemy import orm

from app import db


class User(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sql.String(64), index=True, unique=True)
    
    email: orm.Mapped[str] = orm.mapped_column(sql.String(120), index=True, unique=True)
    
    password_hash: orm.Mapped[str | None] = orm.mapped_column(sql.String(256))

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(back_populates='author')

    def __repr__(self) -> str:
        return f'<User {format(self.username)}>'


class Post(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sql.String(140))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(User.id), index=True)

    author: orm.Mapped[User] = orm.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f'<Post {format(self.body)}>'