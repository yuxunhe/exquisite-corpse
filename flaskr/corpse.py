from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('corpse', __name__)

@bp.route('/mine')
def mine():
    db = get_db()
    limbs = db.execute(
        'SELECT l.id, body, created, author_id'
        ' FROM limb l JOIN user u ON l.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('corpse/mine.html', limbs=limbs)

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
            return redirect(url_for('corpse.mine'))

    return render_template('corpse/create.html')
