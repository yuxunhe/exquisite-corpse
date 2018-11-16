from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('corpse', __name__)

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    limb_text = db.execute(
        'SELECT body FROM limb ORDER BY created DESC'
    ).fetchone()

    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO limb (body, author_id)'
                ' VALUES (?, ?)',
                (body, g.user['id'])
            )
            db.commit()
    return render_template('corpse/new_limb.html')

@bp.route('/mine')
def mine():
    db = get_db()
    user_id = session.get('user_id')
    corpse_ids = db.execute(
        'SELECT corpse_id FROM limb'
        'WHERE author_id = ?'
        'ORDER BY created DESC' (user_id)
    ).fetchall()
    corpses = []
    for corpse_id in corpse_ids:
        corpses.append(
            ("\n").join(db.execute(
                'SELECT body from limb'
	            'WHERE corpse_id = ?'
	            'ORDER BY created DESC' (corpse_id)
            ).fetchall())
        )
    return render_template('corpse/mine.html', corpses = corpses)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO limb (body, author_id)'
                ' VALUES (?, ?)',
                (body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('corpse.index'))

    return render_template('corpse/create.html')
