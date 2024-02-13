import logging

from flask import render_template, Blueprint, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.exceptions import HTTPException

from scaffold import db
from scaffold.models import User
from scaffold.core.forms import LoginForm, ContactForm
from scaffold.utilities.ses import Ses


core = Blueprint('core', __name__)
logger = logging.getLogger('scaffold')


# Routes
@core.route('/')
def index():
    return render_template('index.html')

@core.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar()

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

@core.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        email = form.email.data
        subject = form.name.data + ' contact form submission'
        body = form.message.data
        body_html = f'''
                <html>
                <head></head>
                <body>
                <h1>{subject}</h1>
                <p>
                {body}
                </p><br>
                <p>Sent from: {email}</p>
                </body>
                </html>
            '''

        # Instantiate the SES wrapper.
        ses = Ses()

        # Send an email to your verified SES email address.
        email_1 = ses.send_email(subject=subject,
                                 body=body,
                                 body_html=body_html,
                                 client_address=ses.email)
        
        if email_1:  # Only send user email if we got their message.
            # Send an email to the user acknowledging receipt of their message.
            subject = 'Thanks for contacting us.'
            body = f'''
                This is an automated response confirming our receipt of your
                contact form submission. Please do not reply to this message, as
                replies are not monitored for this address. Your message will be
                reviewed by a human and we'll get back to you soon!
            '''
            body_html = f'''
                <html>
                <head></head>
                <body>
                <h1>{subject}</h1>
                <p>
                {body}
                </p><br>
                <p>Best Regards,</p>
                <p>Mailbot</p>
                </body>
                </html>
            '''
            email_2 = ses.send_email(subject=subject,
                                    body=body,
                                    body_html=body_html,
                                    client_address=email)

        if email_1 and email_2:  # If either email failed, user should know.
            return render_template('contact_thanks.html')
        else:
            return render_template('email_problem.html')
    
    return render_template('contact.html', form=form)

# Exceptions
@core.app_errorhandler(HTTPException)
def error(e):
    """
    Catchall for HTTPExceptions; shows the custom error page with the code.
    """
    return render_template('error.html', code=e.code)
