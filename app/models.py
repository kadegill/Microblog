from datetime import datetime, timezone
from hashlib import md5

import sqlalchemy as sql
from flask_login import UserMixin
from sqlalchemy import Select, orm
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

followers = sql.Table(
    'followers',
    db.metadata,
    sql.Column('follower_id', sql.Integer, sql.ForeignKey('user.id'), primary_key=True),
    sql.Column('followed_id', sql.Integer, sql.ForeignKey('user.id'), primary_key=True)
)


@login.user_loader
def load_user(id: str):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sql.String(64), index=True, unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sql.String(120), index=True, unique=True)
    password_hash: orm.Mapped[str | None] = orm.mapped_column(sql.String(256))

    about_me: orm.Mapped[str | None] = orm.mapped_column(sql.String(140))
    last_seen: orm.Mapped[datetime | None] = orm.mapped_column(sql.DateTime, index=True, default=lambda: datetime.now(timezone.utc)) 
    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(back_populates='author')

    following: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )
    followers: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following'
    )

    def __repr__(self) -> str:
        return f'<User {format(self.username)}>'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str | None) -> bool:
        if self.password_hash is None or password is None:
            return False
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int) -> str:
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user: 'User') -> None:
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user: 'User') -> None:
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user: 'User') -> bool:
        query = self.following.select().where(User.id ==  user.id)
        return db.session.scalar(query) is not None

    def followers_count(self) -> int | None:
        query = sql.select(sql.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self) -> int | None:
        query = sql.select(sql.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self) -> Select['Post']:
        Author = orm.aliased(User)
        Follower = orm.aliased(User)
        return (
            sql.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sql.or_(
                Follower.id == self.id,
                Author.id == self.id,
                ))
                .group_by(Post) # type: ignore
            .order_by(Post.timestamp.desc())
        )

class Post(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sql.String(140))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(User.id), index=True)

    author: orm.Mapped[User] = orm.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f'<Post {format(self.body)}>'