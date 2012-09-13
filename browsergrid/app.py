#!/usr/bin/env python
from __future__ import with_statement
from .models import db, Job
from flask import (Flask, request, session, g, redirect, url_for, abort,
     render_template, flash, Blueprint, current_app)
from .default_settings import Settings
from .forms import NewJobForm, create_browser_choices

bg = Blueprint('bg', __name__)

def create_app(conf_obj=Settings, envvar='BG_SETTINGS'):
    app = Flask(__name__)
    app.config.from_object(conf_obj)
    app.config.from_envvar(envvar, silent=True)
    db.init_app(app)
    app.register_blueprint(bg)
    return app

def init_db(app):
    """Creates the database tables."""
    with app.app_context():
        db.create_all()

@bg.route('/')
def index():
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs)

@bg.route('/new', methods=['GET', 'POST'])
def new():
    form = NewJobForm()
    form.checks.choices = create_browser_choices(current_app.config['BROWSER_OPTIONS'])
    if form.validate_on_submit():
        job = Job.new(url=form.url.data)
        for check in form.checks.data:
            p, bn, ver = check.split('-', 3)
            job.add_check(
                browser_name = bn,
                version = ver,
                platform = p,
            )
        db.session.commit()
        return redirect(url_for('.job_detail', _id = job.id))
    return render_template('new.html', form=form)

@bg.route('/job/<int:_id>')
def job_detail(_id):
    job = Job.query.get_or_404(_id)
    return render_template('job_detail.html', job=job)

app = create_app()

if __name__=="__main__":
    app.run()
