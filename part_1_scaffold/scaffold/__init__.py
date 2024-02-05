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
