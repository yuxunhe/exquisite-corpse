from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from exquisitecorpse.auth import login_required
from exquisitecorpse.db import db, User, Limb, Corpse
import random

bp = Blueprint('corpse', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index(): #add a limb
    if Limb.query.all() == None:
        return render_template('corpse/new-corpse-prompt.html.j2')
    if request.method == 'GET':
        # Fetch last limb from random corpse
        session['limb'] = random.choice(Limb.query.all())
        print("retrived corpse: " + limb.corpse.id)
    #This part actually handles the posting
    if request.method == 'POST':
        body = request.form['body']
        if not body:
            flash("Content is required")
        else:
            user_id = None
            if g.user:
                user_id = g.user['id']
            new_limb = Limb(author_id=user_id, corpse_id=session['limb'].corpse_id, body=body, completed=False)
            print("posted id: " + session["limb"].corpse.id)
            #Check if the corpse has been completed and update the record
            if session['limb'].corpse.limbs.count() >= 5:
                new_limb.completed=True
            db.session.add(new_limb)
            db.session.commit()
        return redirect(url_for('corpse.index'))
    return render_template('corpse/new_limb.html.j2', prompt = session['limb'].body)

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
    return render_template('corpse/mine.html.j2', header = "My Contributions", corpses = corpses)

@bp.route('/randomone')
def randomone():
    db = get_db()
    rows = db.execute(
        'SELECT id FROM corpse WHERE completed = 1 ORDER BY id DESC'
    ).fetchall()
    if len(rows) == 0:
        return render_template('corpse/mine.html.j2', corpses = [])
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
    return render_template('corpse/mine.html.j2', header = "A Random Corpse", corpses = corpses)


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

    return render_template('corpse/create.html.j2')
