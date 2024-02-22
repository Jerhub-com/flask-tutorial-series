# Jerhub Flask Tutorial Series
**Author:** Jeremy Ecker

**Link:** [Jerhub Flask Tutorial Series](https://jerhub.com/tutorials/home)
--

# flask-recaptcha - Instructions for adding Google Recaptcha to a Flask app
Welcome to part 2 of the Jerhub tutorial series. In this part, we are going to
address an issue we have with what we did in part 1: bot mitigation. Google
provides an answer to this in the form of ReCaptcha, which we will show you how
to integrate into your Flask app in this section. This will be a much shorter
section than some of the others, but it is an important one because any time you
have a form into which users can input data, you want to try to prevent bots
from being able to spam the form with potentially malicious requests or trying
to brute-force entry. In future sections, we will be implementing more forms for
other purposes, so we want to have a solid foundation laid out to make it easy
on us.

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

## Final thoughts
See? This one was relatively easy compared to the first part of the tutorial,
which was kind of a lot. Still, this step is important so that we can keep our
forms as secure as possible moving forward. In the next section, we are going to
put what we learned here into practice, as we learn to build one of the most
common components of any website: the contact form.
