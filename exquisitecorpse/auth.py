import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from exquisitecorpse import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        re_entered_password = request.form['re-entered-password']
        error = False
        if not username:
            flash('Username is required.')
            error = True
        if not password:
            flash('Password is required.')
            error = True
        if not re_entered_password:
            flash('Please confirm password.')
            error = True
        if User.query.filter_by(username=username).first() is not None:
            flash('User {} is already registered.'.format(username))
            error = True
        if password != re_entered_password:
            flash("Passwords do not match.")
            error = True
        if error is False:
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(username=username)
            session.clear()
            session['user_id'] = user['id']
            flash("You are now registered!")
            flash("Logged in successfully")
            return redirect(url_for('index'))
    return render_template('auth/register.html.j2')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = False
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash('Incorrect username.')
            error = True
        elif not check_password_hash(user.password, password):
            flash('Incorrect password.')
            error = True

        if error is False:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
    return render_template('auth/login.html.j2')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
