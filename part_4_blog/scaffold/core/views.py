import logging
import os
import datetime

from flask import render_template, Blueprint, url_for, redirect, current_app, send_from_directory, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.exceptions import HTTPException
from flask_ckeditor import upload_success, upload_fail

from scaffold import db
from scaffold.models import User, BlogPost
from scaffold.core.forms import LoginForm, ContactForm, BlogPostForm
from scaffold.utilities.ses import Ses


core = Blueprint('core', __name__)
logger = logging.getLogger('scaffold')


# Routes (basic) ---------------------------------------------------------------
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

# Routes (blog posts) ----------------------------------------------------------
@core.route('/blog')
def blog():
    """
    Display published blog posts to users.
    """
    posts = db.session.execute(db.select(BlogPost).filter_by(published=True).order_by(BlogPost.date.desc())).scalars()

    return render_template('blog/blog.html', posts=posts)

@core.route('/blog/admin')
@login_required
def blog_admin():
    """
    Display all blog posts to admins.
    """
    if not current_user.admin:
        abort(403)

    posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.date.desc())).scalars()

    return render_template('blog/blog_admin.html', posts=posts)

@core.route('/files/<path:filename>')
def uploaded_files(filename):
    """
    Uploaded files for CKEditor.
    Reference:
    https://flask-ckeditor.readthedocs.io/en/latest/plugins.html#image-upload
    """
    path = current_app.config['UPLOADED_PATH']

    return send_from_directory(path, filename)

@core.route('/upload', methods=['POST'])
@login_required
def upload():
    """
    Upload an image for CKEditor.
    Reference:
    https://flask-ckeditor.readthedocs.io/en/latest/plugins.html#image-upload
    """
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()

    if extension not in ['jpg', 'png']:
        return upload_fail(message='jpg or png image only.')
    
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
    url = url_for('core.uploaded_files', filename=f.filename)

    return upload_success(url, filename=f.filename)

@core.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """
    Create a new blog post if the user is an admin.
    """
    if not current_user.admin:
        abort(403)
    
    form = BlogPostForm()

    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(id=current_user.id)).scalar()
        date = datetime.datetime.now()
        blog_post = BlogPost(user=user.username,
                             date=date,
                             title=form.title.data,
                             content=form.content.data,
                             published=False)
        
        db.session.add(blog_post)
        db.session.commit()

        return redirect(url_for('core.blog'))
    
    return render_template('blog/create_post.html', form=form)

@core.route('/<int:post_id>')
def read_post(post_id):
    """
    View individual blog posts based on the post id.
    """
    blog_post = db.session.execute(db.select(BlogPost).filter_by(id=post_id)).scalar()

    # The post must be published in order to be publicly visible.
    if blog_post.published or current_user.admin:
        return render_template('blog/read_post.html', post=blog_post)
  
    else:                
        abort(404)


@core.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    """
    Allow admin to edit a blog post.
    """
    if not current_user.admin:
        abort(403)

    blog_post = db.session.execute(db.select(BlogPost).filter_by(id=post_id)).scalar()

    form = BlogPostForm()

    if form.validate_on_submit():
        blog_post.title=form.title.data
        blog_post.content=form.content.data
        db.session.commit()

        return redirect(url_for('core.read_post', post_id=blog_post.id))
    
    # Pre-populate the form with current data
    elif request.method == 'GET':
        form.title.data = blog_post.title
        form.content.data = blog_post.content

    return render_template('blog/create_post.html', form=form)
    
@core.route('/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    """
    Allow admin to delete a blog post.
    """
    if not current_user.admin:
        abort(403)
    
    blog_post = db.session.execute(db.select(BlogPost).filter_by(id=post_id)).scalar()

    db.session.delete(blog_post)
    db.session.commit()

    return redirect(url_for('core.blog'))

@core.route('/<int:post_id>/publish', methods=['GET', 'POST'])
@login_required
def publish_post(post_id):
    """
    Toggle a blog post's published flag.
    """
    if not current_user.admin:
        abort(403)

    blog_post = db.session.execute(db.select(BlogPost).filter_by(id=post_id)).scalar()
    
    blog_post.published = False if blog_post.published else True
    blog_post.date = datetime.datetime.utcnow()

    db.session.commit()

    return redirect(url_for('core.read_post', post_id=post_id))

# Exceptions -------------------------------------------------------------------
@core.app_errorhandler(HTTPException)
def error(e):
    """
    Catchall for HTTPExceptions; shows the custom error page with the code.
    """
    return render_template('error.html', code=e.code)
