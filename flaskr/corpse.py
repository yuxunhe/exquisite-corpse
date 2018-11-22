from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import random

bp = Blueprint('corpse', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index(): #add a limb
    db = get_db()
    #This part selects the prompt to be displayed
    rows = db.execute(
        'SELECT id FROM corpse WHERE completed = 0 ORDER BY id DESC'
    ).fetchall() #1 is true!
    if len(rows) == 0:
        return redirect(url_for('corpse.no_corpse_available'))
    if request.method == 'GET':
        row = random.choice(rows)
        corpse_id = row["id"]
        session["corpseId"] = corpse_id
        print("retrived id: %d" %(corpse_id))
        limb_rows= db.execute(
            'SELECT body FROM limb WHERE corpse_id = (?) ORDER BY created DESC', (corpse_id,)
        ).fetchall()
        limb = limb_rows[0][0]
        session["limb"] = limb
        session["row_size"] = len(limb_rows)
    #This part actually handles the posting
    if request.method == 'POST':
        body = request.form['body']
        error = None
        if not body:
            error = 'Content is required.'
        if error is not None:
            flash(error)
        else:
            #db = get_db()
            user_id = "NULL"
            if g.user:
                user_id = g.user['id']
            print("posted id: %d" %(session["corpseId"]))
            db.execute(
                'INSERT INTO limb (body, author_id, corpse_id, completed)'
                ' VALUES (?, ?, ?, ?)',
                (body, user_id, session["corpseId"], 0)
            )
            db.commit()
        #Check if the corpse has been completed and update the record
        if session["row_size"] >= 5:
            db.execute(
                'UPDATE corpse SET completed = 1 WHERE id = (?)', (session["corpseId"],)
            )
            db.commit()
        return redirect(url_for('corpse.index'))
    return render_template('corpse/new_limb.html', prompt = session["limb"])

@bp.route('/mine')
def mine():
    db = get_db()
    user_id = session.get('user_id')
    rows = db.execute(
        'SELECT id FROM corpse WHERE author_id = ? ORDER BY id DESC', (g.user['id'],)
    ).fetchall()
    corpses = []
    for row in rows:
        corpse_id = row['id']
        limbs = []
        limb_rows = db.execute(
        'SELECT body from limb WHERE corpse_id = ? ORDER BY created ASC', (corpse_id,)
        ).fetchall()
        for row in limb_rows:
            limbs.append(row[0])
        corpses.append(
            ("<br/>").join(limbs)
        )
    return render_template('corpse/mine.html', header = "My Contributions", corpses = corpses)

@bp.route('/randomone')
def randomone():
    db = get_db()
    rows = db.execute(
        'SELECT id FROM corpse WHERE completed = 1 ORDER BY id DESC'
    ).fetchall()
    if len(rows) == 0:
        return render_template('corpse/mine.html', corpses = [])
    random.shuffle(rows)
    row = rows[0]
    corpse_id = row['id']
    limbs = []
    limb_rows = db.execute(
        'SELECT body from limb WHERE corpse_id = ? ORDER BY created ASC', (corpse_id,)
    ).fetchall()
    for row in limb_rows:
        limbs.append(row[0])
    corpses = []
    corpses.append(
        ("<br/>").join(limbs)
    )
    return render_template('corpse/mine.html', header = "A Random Corpse", corpses = corpses)


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
                'INSERT INTO corpse (author_id) VALUES (?)',
                (g.user['id'],)
            )
            corpse_id = db.execute('SELECT id from corpse ORDER BY id DESC').fetchone()
            db.execute(
                'INSERT INTO limb (body, author_id, corpse_id, completed)'
                ' VALUES (?, ?, ?, ?)',
                (body, g.user['id'], corpse_id['id'], 0)
            )
            db.commit()
            return redirect(url_for('corpse.index'))

    return render_template('corpse/create.html')

@bp.route('/no_corpse_available')
def no_corpse_available():
    return render_template('corpse/new-corpse-prompt.html')
