from urllib.parse import urlsplit

import sqlalchemy as sql
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import LoginForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Kaden'}    # Mock user
    posts = [
        {
            'author': {'username': 'Kaden'},
            'body': 'This is a mock post.'
        },
        {
            'author': {'username': 'Baden'},
            'body': 'This is another mock post.'
        },
        {
            'author': {'username': 'Daden'},
            'body': 'This is another another mock post.'
        },
        {
            'author': {'username': 'Eaden'},
            'body': 'This is yet another mock post.'
        }
    ]
    return render_template('index.html', posts=posts, title='Home Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sql.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
