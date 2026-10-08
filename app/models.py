from datetime import datetime, timezone

import sqlalchemy as sql
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


@login.user_loader
def load_user(id: str):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sql.String(64), index=True, unique=True)
    
    email: orm.Mapped[str] = orm.mapped_column(sql.String(120), index=True, unique=True)
    
    password_hash: orm.Mapped[str | None] = orm.mapped_column(sql.String(256))

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(back_populates='author')

    def __repr__(self) -> str:
        return f'<User {format(self.username)}>'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str | None) -> bool:
        if self.password_hash is None or password is None:
            return False
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sql.String(140))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(User.id), index=True)

    author: orm.Mapped[User] = orm.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f'<Post {format(self.body)}>'