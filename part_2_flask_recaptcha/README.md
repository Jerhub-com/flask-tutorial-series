# flask-recaptcha - Instructions for adding Google Recaptcha to a Flask app

This is not standalone, but meant to be added to an existing app (i.e.
flask-scaffold). If you are following along with Jerhub's tutorials, you should
first clone the flask-scaffold repository and test that it runs correctly on
your local machine, and then follow these instructions. The end result will be
the addition of recaptcha to the login form.

[Get Jerhub's flask-scaffold](https://github.com/Jerhub-com/flask-scaffold)

## Step 1: Get Recaptcha keys
See the Google Recaptcha documentation to setup your keys:
[see the docs](https://developers.google.com/recaptcha/docs/v3)

## Step 2: Add keys to environment variables
If you followed along with part 1 of this series, you know how to do this
already. If not, you can refer to that tutorial. In this example, we are naming
the variables as follows:
```
RECAP_PUBLIC_KEY=your_public_key
RECAP_PRIVATE_KEY=your_private_key
```

## Step 3: Add the environment variables to your app
Add the following to your `__init__.py` file, after initializing the app:
```
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAP_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAP_PRIVATE_KEY')
app.config['RECAPTCHA_DATA_ATTRS'] = {'size': 'compact'}
```
Here we adjust the size of the widget to compact so that it will look better on
mobile devices.

## Step 4: Add a ReCaptcha field to the form
Locate the `core/forms.py` file and add `flask_wtf.RecaptchaField` to the
imports, for example:
```
from flask_wtf import RecaptchaField
```
Next, add the field to the form as the final field after submit:
```
recaptcha = RecaptchaField()
```
Finally, put the field in the HTML form in `templates/login.html`:
```
{{form.recaptcha}}
```
