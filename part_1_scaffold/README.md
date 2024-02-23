# Jerhub Flask Tutorial Series
**Author:** Jeremy Ecker

**Link:** [Jerhub Flask Tutorial Series](https://jerhub.com/tutorials/home)
--

# Part 1: Scaffold
Covers installation and configuration, and provides the foundation from which we
build the application, including a basic app with a sqlite database, a user
model, and a login page.

## Installation and Configuration
These instructions will show how you can run the application. These will be
applicable to each section of this tutorial, so you can refer back to this
document if you forget some detail. Each new section may introduce new steps
or additions to this, but this section demonstrates the basic ideas you will
need to understand.

### Clone the repository
```
git clone https://github.com/Jerhub-com/flask-tutorial-series.git
```

### Create a virtual environment
```
python -m venv venv
```

### Create a secret key for Flask
You can use any key for this, but it should be something difficult to guess or
crack. If you aren't feeling creative, you can use `generate_secret.py` to make
one.
```
python generate_secret.py
```

### Add the secret key as an environment variable
**What are environment variables?**
[Wikipedia article](https://en.wikipedia.org/wiki/Environment_variable)

**How do I define them?**
Different operating systems have different ways of setting these, so it depends
on your environment which way you will need to follow. For the purpose of this
document, we will show two ways: adding them to the Python virtual environment
via the activation script on Windows, and a `.env` file for the Linux production
server.


**Important note:** do not include the environment variables in your source
control, as this is a security risk. Make sure to add the `venv` directory, or
the `.env` file to your `.gitignore`, for example:
```
**/venv
.env
```

**Windows: Python virtual environment**

Locate the script that you use to activate your virtual environment. In the
flask-scaffold example, this will be located at `venv\Scripts\activate.bat`.

Scroll down to the bottom of the file, and add the variables using the `set`
command, for example:
```
set FLASK_SECRET_KEY=your_flask_secret_key
```

Save the file, and the next time you run the activation script, the virtual
environment will be aware of them.

**Linux: .env file**

Create a file named `.env` at the root directory of your project, and add the
variables there:
```
FLASK_SECRET_KEY=your_flask_secret_key
```

### Activate the virtual environment (Windows)
```
venv\Scripts\activate.bat
```

### Activate the virtual environment (Linux)
```
source venv/bin/activate
```

### Install the required packages
```
pip install -r requirements.txt
```

### Database initialization
```
flask db init
flask db migrate
flask db upgrade
```

### Running the application
```
python app.py
```

### Create an admin user
Open a separate terminal and use flask shell to create your admin user:
```
flask shell
>>> from create_admin import CreateAdmin
>>> admin = CreateAdmin('Bob', 'bob@example.com')
Here is your login info; please store it someplace safe.
Username: Bob
Email: bob@example.com
Password: super-secret-password <-- Write this down; you won't see it again.
>>> exit()
```

### Visiting your web app

- Open a web browser
- Navigate to `http:your_IP_address:5000`, for example:
```
http:192.168.1.100:5000
```
To find the local IP address of your machine, you can do:

**(Windows)**
```
ipconfig
```

**(Linux)**
```
ifconfig
```

## Application structure
Hopefully everything went well up to this point. We are now ready to begin
building our app. This will be a large section, because we are going to cover
a lot of ground here. The hope is that, armed with this knowledge, you will be
ready to follow along with the more complicated sections ahead.

First thing's first, go ahead and close out of any running instances of the
provided app, since now that you know you can run it, you are going to build it
yourself from scratch.

Create a new folder somewhere on your machine, and open it with your code
editor. It doesn't matter what you name it - be creative!

Next, we will create a folder within your working folder called `scaffold`. This
folder will contain the majority of our code.

Next to the scaffold folder, create a new file called `app.py`. This is the file
which we will execute to run our app. Within app.py, you can paste this code:
```
from scaffold import app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

**Important Note:** Make sure to remove the `debug=True` prior to deploying to
a publicly accessible server. We have enabled it for local development in order
to help troubleshoot any errors, but having it enabled on a public server
introduces security risks.

Sounds pretty good so far, but the scaffold folder doesn't yet contain anything.
Let's fix that. Within the scaffold folder, we will create a new file called
`__init__.py` (note the double underscores), then paste the following code
within:
```
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect


# Initialize app----------------------------------------------------------------
app = Flask(__name__)
app.logger.warning(f"How to use the logger:\nlogger = logging.getLogger('scaffold')")
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

# Database Setup----------------------------------------------------------------
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

# CSRF--------------------------------------------------------------------------
csrf = CSRFProtect(app)

# Login Configuration-----------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'core.login'

# Blueprint Registrations-------------------------------------------------------
from scaffold.core.views import core

app.register_blueprint(core)
```

Right beside `__init__.py`, create another file called `models.py`. This is
where we will put database related code. Inside models, you will make the first
model, which will be a User:
```
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from scaffold import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean(), default=False)

    def __init__(self, username, email, password, admin):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.admin = admin

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

Next, create new directories within scaffold called `core`, `static` and
`templates`. Static and templates have names with meanings special to Flask -
templates is where the HTML files will live, and static is where we will place
files such as images, CSS, and JS. Core is where we will define our views and
forms.

Inside core, create a file `views.py`, and put this code:

```
import logging

from flask import render_template, Blueprint

core = Blueprint('core', __name__)
logger = logging.getLogger('scaffold')


@core.route('/')
def index():
    return render_template('index.html')
```

We'll take a moment now to go over what we've done so far. At this point you
should have an application structure that looks like this:

```
main folder
    scaffold
        core
            views.py
        static
        templates

        __init__.py
        models.py
    app.py
```

We aren't quite ready to try running the app just yet, because we are still
missing an important piece: templates.

## Templates
With the templates, we are going to have every page in the application share
some common traits, such as the navigation bar at the top, styling, and the
footer at the bottom. Rather than make every html file repeat these, we will
make one single base template, and then each of the templates for specific
pages will inherit from the base, so they will only need to add code which is
unique to that page.

Inside the templates folder, create a file called `base.html`, and place this
code within:
```
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Flask Scaffold</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
        <link rel="stylesheet" href="{{url_for('static', filename='styles/base.css')}}">
        <link rel="shortcut icon" href="{{url_for('static', filename='icons/favicon.ico')}}">
    </head>

    <body>

    <nav class="navbar navbar-expand-sm bg-dark navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href={{url_for('core.index')}}>
                <img src="{{url_for('static', filename='site_images/jerhub_logo.png')}}" style="width:100px; height: 100px;">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#collapsibleNavbar">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="collapsibleNavbar">
                <ul class="navbar-nav">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href={{url_for('core.logout')}}>Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href={{url_for('core.login')}}>Login</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% block content %}
    {% endblock %}

    <hr>
    <ul class="nav justify-content-center border-bottom pb-3 mb-3">
        <li class="nav-item"><a href={{url_for('core.index')}} class="nav-link px-2 text-muted">Home</a></li>
    </ul>

    <p class="text-center text-muted">Copyright &copy;
        <script>
          document.write(new Date().getFullYear())
        </script>
        Jerhub - All Rights Reserved
      </p>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>

    </body>
</html>
```

Observe that we are using Bootstrap here for styling, because we are focusing
on backend integrations in this tutorial. Make sure that the bootstrap you are
using is up to date prior to deploying to production, specifically double check
on their documentation that your script sources are accurate:
[bootstrap documentation](https://getbootstrap.com/docs/5.3/getting-started/introduction/).

Observe also that even though we use bootstrap for most things, we are going to
add just a tiny bit of custom CSS of our own. This is where the `static` folder
comes into play. Within `scaffold/static` let's create a new folder and call it
`styles`. Within styles create a file `base.css`:
```
.flex-container {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: space-around;
    align-content: center;
    align-items: center;
    margin: 0 auto;
    gap: 10px;
    padding: 10px 10px;
}

.card {
    display: flex;
    border-radius: 5px;
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    padding: 20px 20px;
}

.center-image {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 50%;
}
```

Okay, it isn't going to win any awards, but this should be enough to make it
responsive and tolerable to the eye.

Next, make a new directory `scaffold/static/site_images`, and within that, you
should place a picture to use as your logo. If you want, you can use
`jerhub_logo.png` which is included with this repository. Same thing goes for
the `favicon.ico` - make a `scaffold/static/icons` folder and put your favicon
there. Note that if you used your own files for this, you may need to change the
names in `base.html` to match your files.

We are getting close to being done with this section now, just a couple of more
steps. Remember when we said that we would make templates which inherit from
the base template, and then use those to display the page content? Well, let's
do it, starting with `index.html`:
```
{% extends 'base.html' %}
{% block content %}

<br>
<div class="flex-container">
    <div class="card">
        <p>Your Flask Scaffold is working correctly.</p>
    </div>
    <div class="card">
        <p>Happy Hacking!</p>
    </div>
</div>

{% endblock %}
```

This is the basic pattern which we will use for all the future html templates
we make - inside base.html, you notice the two lines right next to each other:
```
{% block content %}
{% endblock %}
```

This is the Jinja way of saying we are going to put something here from
somewhere else, in this case index.html. We tell jinja that this is the case
by declaring that the template `extends` base, and we tell it where on the page
to display the content by using the `block` statement with the same name as
what was declared in base, in this case we called it `content`. Jinja is pretty
powerful - you'll notice that we can display things contextually such as with
`if` statements, etc. For more information, the Flask documentation has some
great info and examples. We aren't going to dive too deep into it here since
we really are focusing on backend integrations, but it is good to understand at
least the basics of jinja, so here is a link to some good info:
[Flask template docs](https://flask.palletsprojects.com/en/3.0.x/templating/).

As an aside, Flask has really good documentation in general, so we highly
recommend using it as a reference any time you get confused about what is going
on in this tutorial.

Next, let's finish up with our templates. We need a few more templates for this
section:

- bad_login.html - displays when a user enters incorrect login info
- error.html - displayed when an error is encountered such as a 404, etc
- login.html - this is for the login route, which we will cover shortly
- welcome.html - displayed after a successful login

These files are provided, so you can try to implement them yourself, and refer
to the provided files if you get stuck. A couple of hints:

- For error.html, observe in views.py that we are providing the error code to
the call to render_template. You can then use that information from within the
template if you wish using the double curly braces `{{}}` and the variable name.
- For the login page we will be designing a form which the user will fill out,
so it might make more sense after we've done that. So let's do it right now.

## Login form
Create a new file `scaffold/core/forms.py`:
```
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField('Log In')
```

The names of these fields are what we are using in the login template, along
with `hidden_tag`, which is a special hidden form field which WTForms uses to
provide CSRF (Cross-Site Request Forgery) protection. Remember in `__init__.py`,
we called csrf protect on our app, so this is where we use it in `login.html`:
```
{% extends 'base.html' %}
{% block content %}

<div class="flex-container">
    <div class="card">
        <h1>Login</h1><br>
        <form method="POST">
            {{form.hidden_tag()}}
            {{form.email.label}}<br>
            {{form.email}}<br><br>
            {{form.password.label}}<br>
            {{form.password}}<br><br>
            {{form.submit()}}
        </form>
    </div>
</div>

{% endblock %}
```

Time to revisit `views.py` and put this all together:
```
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

@core.app_errorhandler(HTTPException)
def error(e):
    """
    Catchall for HTTPExceptions; shows the custom error page with the code.
    """
    return render_template('error.html', code=e.code)
```

In the login function, we check to see if the user exists in the database, then
whether the password they entered is valid. If so, we redirect them to the
welcome page. If not, we display the bad login page. If the form was not
submitted yet, we skip that and display the login form.

And that's basically it for this section.

## Final thoughts
That was a lot to take in, so if you got this far then you should be proud of
yourself! A couple of things to note:

- If you are using version control, please do make a `.gitignore` file to
exclude any files or directories which may contain data which should be private.
I know we've discussed that earlier, but it bears repeating because it is
important for security.
- Use virtual environments. Use different ones for each section. Use a 
`requirements.txt` file to help keep track of your dependencies.
- Refer back to this document as you proceed with the next parts of this
tutorial series, as it provides the foundation upon which we build everything
else.
- Official documentation is your friend. Use it to understand the things which
may have you scratching your head.
- Experiment! Play around with the things you are learning, it will help you
to understand, and to keep the inspiration flowing.
- Take breaks. When the brain is full, it needs time to process the new info, so
give it that time and come back fresh later.

One last thing, you may have noticed that our login form, while it does have at
least CSRF protection, does not have any way to prevent bots from spamming it.
Don't worry - we will address this issue in Part 2: ReCaptcha.
