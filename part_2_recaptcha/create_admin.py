import secrets

from scaffold import db
from scaffold.models import User


class CreateAdmin():
    '''
    Create a User with Admin set to True. Meant to be used from within a flask
    shell. Automatically generates a password for the user, which you must store
    someplace safe since you won't be able to see it again.

    Usage:
        admin = CreateAdmin('Bob', 'bob@example.com')
    '''
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.password = secrets.token_urlsafe(16)
        self.admin = True
        
        user = User(username=self.username,
                    email=self.email,
                    password=self.password,
                    admin=self.admin)
        
        db.session.add(user)
        db.session.commit()

        print('Here is your login info; please store it someplace safe.')
        print(f'Username: {self.username}')
        print(f'Email: {self.email}')
        print(f'Password: {self.password}')
