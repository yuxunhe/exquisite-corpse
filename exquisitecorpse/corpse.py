from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from exquisitecorpse.auth import login_required
from exquisitecorpse.db import db, User, Limb, Corpse
import random
import datetime

bp = Blueprint('corpse', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index(): #add a limb
    if Limb.query.first() == None:
        return render_template('corpse/new-corpse-prompt.html.j2')
    if request.method == 'GET':
        # Fetch last limb from random corpse
        limb = random.choice(Limb.query.all())
        session['limb_id'] = limb.id
    #This part actually handles the posting
    if request.method == 'POST':
        body = request.form['body']
        if not body:
            flash("Content is required")
        else:
            user_id = None
            if g.user:
                user_id = g.user.id
            new_limb = Limb(author_id=user_id, corpse_id=session.get('limb_id'), created=datetime.datetime.now(), body=body, completed=False)
            # TODO: Check if the corpse has been completed and update the record
            # The relationship needs to be queried correctly through SQLalchemy
            # if Limb.query.join(Corpse).join(Limb).filter_by(id=session.get('limb_id')).corpses.limbs.count() >= 5:
            #     new_limb.completed=True
            db.session.add(new_limb)
            db.session.commit()
        return redirect(url_for('corpse.index'))
    return render_template('corpse/new_limb.html.j2', prompt = limb.body)

@bp.route('/mine')
def mine():
    user = User.query.filter_by(id=g.user.id).first()
    return render_template('corpse/mine.html.j2', header = "My Contributions", corpses = user.corpses)

@bp.route('/random')
def randomone():
    corpse = random.choice(Limb.query.all())
    return render_template('corpse/mine.html.j2', header = "A Random Corpse", corpses = corpse)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        body = request.form['body']
        if not body:
            flash('Content is required.')
        else:
            new_corpse = Corpse(author_id=g.user.id)
            new_limb = Limb(author_id=g.user.id, corpse_id=new_corpse.id, created=datetime.datetime.now(), body=body, completed=False)
            db.session.add(new_corpse)
            db.session.add(new_limb)
            db.session.commit()
            return redirect(url_for('corpse.index'))

    return render_template('corpse/create.html.j2')
