import os
import io
from datetime import datetime, timedelta

from flask import flash, render_template, request, redirect, url_for, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField
from flask_admin import AdminIndexView
import flask_security as security
from flask_security.utils import encrypt_password
import flask_login as login
from flask_login import login_required
from wtforms.fields import PasswordField
from sqlalchemy import Date, cast

import numpy as np
from sklearn.metrics import roc_auc_score

from app import app, security, db
from models import User, Competition, Submission


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submission', methods=['GET', 'POST'])
@login_required
def upload_file():

    try:

        now = datetime.now()
        
        competitions = [c for c in Competition.query.all() if (not c.start_on or
            c.start_on <= now) and (not c.end_on or c.end_on >= now)]

        if request.method == 'POST':
            
            competition_id = request.form.get('competitions')
            if competition_id == None:
                flash('No competition selected')
                return redirect(request.url)

            user_id = login.current_user.id

            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            # check if the user has made submissions in the past 24h
            if Submission.query.filter_by(user_id=user_id).filter_by(competition_id=competition_id).filter(Submission.submitted_on>now-timedelta(hours=23)).count() > 0:
                flash("You already did a submission in the past 24h.")
                return redirect(request.url)

            if file:

                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # save submission
                submission = Submission()
                submission.user_id = login.current_user.id
                submission.competition_id = competition_id
                submission.filename = filename
                (submission.previewscore, submission.score) = get_scores(filepath, competition_id)
                submission.submitted_on = now.replace(microsecond=0)
                db.session.add(submission)
                db.session.commit()

                return redirect(url_for('scores'))

        return render_template('submission.html', competitions=competitions)

    except ParsingError as e:
        flash(str(e))
        return redirect(request.url)


@login_required
def get_scores(filename, competition_id):
    "Returns (previewscore, score)"

    regex = r'(.+),(\d+\.\d+|\d+)'

    # parse files
    predictions = np.fromregex(filename, regex, [('id', 'S128'), ('v0', np.float32)])
    groundtruth_filename = os.path.join(app.config['GROUNDTRUTH_FOLDER'], Competition.query.get(competition_id).groundtruth)
    groundtruth = np.fromregex(groundtruth_filename, regex, [('id', 'S128'), ('v0', np.float32)])

    # sort data
    predictions.sort(order='id')
    groundtruth.sort(order='id')

    if predictions['id'].size == 0 or not np.array_equal(predictions['id'], groundtruth['id']):
        raise ParsingError("Error parsing the submission file. Make sure it has the right format and contains the right ids.")
    
    # partition the data indices into two sets and evaluate separately
    splitpoint = int(np.round(len(groundtruth) * 0.15))
    score_p = roc_auc_score(groundtruth['v0'][:splitpoint], predictions['v0'][:splitpoint])
    score_f = roc_auc_score(groundtruth['v0'][splitpoint:], predictions['v0'][splitpoint:])
    
    return (score_p, score_f)

@app.route('/scores', methods=['GET', 'POST'])
@login_required
def scores():
    competitions = Competition.query.all()
    return render_template('scores.html', competitions=competitions)

@app.route('/_get_submissions', methods=['POST'])
@login_required
def get_submissions():
    if request.method == 'POST':
        competition_id = request.form.get('competitions')
        submissions = Submission.query.filter(Submission.competition_id==competition_id)
#        if not login.current_user.has_role('admin'):
#            submissions = submissions.filter_by(user_id=login.current_user.id)

        count = submissions.count()

        if count == 0:
            return jsonify({"count": 0})

        response = {}

        # get all users
        user_ids = sorted(list({s.user_id for s in submissions}))
        dates = sorted(list({s.submitted_on.date() for s in submissions}))

        rows = ""
        for d in dates:
            row = '{{"c":[{{"v":"Date({0},{1},{2})"}}'.format(d.year, d.month - 1, d.day)
            for u in user_ids:
                s = submissions.filter(cast(Submission.submitted_on, Date)==d).filter(Submission.user_id==u)
                if s.count() > 0:
                    previewscore = s.first().previewscore
                    row += ',{{"v":{:.2f}}}'.format(previewscore * 100)
                else:
                    row += ',{"v":"null"}'
            row += "]},"
            rows += row


        s = """    
        {{   
          "cols": [
                {{"id":"","label":"Date","pattern":"","type":"datetime"}},
                {0}
              ],  
          "rows": [     
                {1}
              ]
        }}""".format(
                ','.join('{{"id":"","label":"{}","pattern":"","type":"number"}}'.format(User.query.get(u).username) for u in user_ids),
                rows
                )

        return jsonify({"count": count, "s": s})


###############
# Admin views #
###############

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return login.current_user.has_role('admin')

class AdminModelView(ModelView):

    def is_accessible(self):
        return login.current_user.has_role('admin')

#    def inaccessible_callback(self, name, **kwargs):
#        # redirect to login page if user doesn't have access
#        return redirect(url_for('security.login', next=request.url))

class UserAdmin(ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return login.current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = encrypt_password(model.password2)


class CompetitionAdmin(AdminModelView):

    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'groundtruth': FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'groundtruth': {
            'label': 'Ground truth',
            'base_path': os.path.join(app.config['GROUNDTRUTH_FOLDER']),
            'allow_overwrite': False
        }
    }
    

@login_required
@app.route('/groundtruth/<filename>')
def get_groundtruth(filename):

    if Competition.query.filter_by(groundtruth=filename).count() == 0:
        abort(404)

    if login.current_user.has_role('admin'):
        return send_from_directory(app.config['GROUNDTRUTH_FOLDER'],
                                   filename)
    else:
        abort(403)

@login_required
@app.route('/submissions/<filename>')
def get_submission(filename):

    submissions = Submission.query.filter_by(filename=filename)
    
    # make sure the current user is whether admin or the user who actually submitted the file    
    if ( submissions.count() > 0 and (login.current_user.has_role('admin') or login.current_user.id == submissions.first().user_id)):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)
    else:
        abort(403)

class Error(Exception):
    pass

class ParsingError(Error):
    pass
