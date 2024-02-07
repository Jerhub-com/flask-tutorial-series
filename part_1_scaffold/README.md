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
git clone https://github.com/Jerhub-com/flask-scaffold.git
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

Next, create a new directory within scaffold called `core`. This directory will
contain the main application code. Create also directories called `static` and
`templates`. These directories have names with meanings special to Flask -
templates is where the HTML files will live, and static is where we will place
files such as images, CSS, and JS.

