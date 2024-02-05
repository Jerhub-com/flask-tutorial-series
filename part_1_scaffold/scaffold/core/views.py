import logging

from flask import render_template, Blueprint, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.exceptions import HTTPException

from scaffold import db
from scaffold.models import User
from scaffold.core.forms import LoginForm


core = Blueprint('core', __name__)
logger = logging.getLogger('scaffold')


@core.route('/')
def index():
    return render_template('index.html')

@core.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('core.welcome'))
            else:
                error = 'Invalid credentials'
                return render_template('bad_login.html', error=error)
        else:
            error = 'Invalid credentials'
            return render_template('bad_login.html', error=error)
        
    return render_template('login.html', form=form)

@core.route('/welcome')
@login_required
def welcome():
    username = current_user.username
    return render_template('welcome.html', username=username)

@core.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index'))

@core.app_errorhandler(HTTPException)
def error(e):
    """
    Catchall for HTTPExceptions; shows the custom error page with the code.
    """
    return render_template('error.html', code=e.code)
