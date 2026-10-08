from flask import flash, redirect, render_template, url_for

from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
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
    return render_template('index.html', user=user, posts=posts, title='Home Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user "{form.username.data}", remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
