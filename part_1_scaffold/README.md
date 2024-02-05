# Part 1: Flask-Scaffold
Covers installation and configuration, and provides the foundation from which we
build the application, including a basic app with a sqlite database, a user
model, and a login page.

## Installation and Configuration

### Clone the repository
```
git clone https://github.com/Jerhub-com/flask-scaffold.git
cd flask-scaffold
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

**Windows Python virtual environment**

Locate the script that you use to activate your virtual environment. In the
flask-scaffold example, this will be located at `venv\Scripts\activate.bat`.


Scroll down to the bottom of the file, and add the variables using the `set`
command, for example:


```
set FLASK_SECRET_KEY=your_flask_secret_key
```

Save the file, and the next time you run the activation script, the virtual
environment will be aware of them.

**Linux .env file**

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

### Database Initialization
```
flask db init
flask db migrate
flask db upgrade
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
