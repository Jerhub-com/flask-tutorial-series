# Part 3: Contact
In this section, we will add a functioning contact form which will send emails
via AWS SES (Simple Email Service).

## Step 1: Review AWS SES documentation and acquire a verified email
In order for this to work, you will require an AWS account, and a verified SES
email. It is advised to review the AWS documentation on this subject prior to
proceeding with this integration. The docs can be found here:
[AWS SES docs](https://docs.aws.amazon.com/ses/latest/dg/setting-up.html).
Check out the tutorials there, which should provide a decent background for
getting setup to send emails with SES.

**IMPORTANT NOTE**: You will need AWS access keys in order to interact
programmatically with SES, and while the SES documentation does a great job of
showing you how to setup SES, it doesn't go into much detail about the fact that
there are different types of keys which are suited for different types of uses.
It is highly recommended at this point to review the documentation:
[AWS Authentication and Access Docs](https://docs.aws.amazon.com/sdkref/latest/guide/access.html), in order to select the best option for your case.

Once you have reviewed these, head over to [sending emails programmatically](https://docs.aws.amazon.com/ses/latest/dg/send-an-email-using-sdk-programmatically.html) and
take a look at the Python example there - this is what we will use as the
pattern for this tutorial.

The AWS documentation is fantastic, so rather than reinvent the wheel by
repeating it here, go ahead and follow their instructions to get yourself setup,
then come back here when you're done and continue with step 2.

## Step 2: Add AWS keys as environment variables
In the AWS SES documentation on sending emails programmatically, you may have
noticed that they suggest setting up a shared credentials file. While this
approach is perfectly valid, we are going to instead add the keys as enviroment
variables. For this tutorial, as we progress, we will add several other types
of integrations which will require secret keys. Rather than having the various
credentials stored all over the place in different files (which it might be easy
to forget to exclude from your version control), we are going to keep them safe
in one central place: the environment variables.

If you've been following along with the previous parts of this tutorial, you
should be an old-hand at this by now. If you forgot how to do it, go back and
review the readme in part 1 of our tutorial. For this example, we are naming the
keys like this:
```
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
```

## Step 3: Create the Python code to handle sending emails
In the example from the SES docs, they showed us everything we need to know in
order to send an email using Python and Boto3. So all we really need to do is
make it clean and useable from within our Flask application. The main things
this class needs to do are:

- Read in the configuration details from the yaml file
- Instantiate a boto3 client
- Send an email

We will create a new directory to house our SES code outside of core, let's call
it `utilities`, and put our `ses_config.yaml` and `ses.py` files there. So our
directory structure should resemble this now:

```
scaffold
    core
    static
    templates
    utilities
        (ses_config.yml and ses.py go here)
```
At this point, it is a good idea to add `scaffold/utilities/ses_config.yml` to
your `.gitignore` file so that the email address is not in your source control.

### Create an SES configuration file
Remember in step 2 when we said we were going to put all of our details in one
place (environment variables)? Well, that is true as far as sensitive private
credentials are concerned. In this case however, we are going to be declaring
some variables which we might want to be able to easily change later on -
specifically the email address and AWS region. So in this case, it makes sense
to stash them in a yaml file which we will read from our app.

Since we are configuring SES, let's call this file `ses_config.yml`:

```
version: 1
email: your_email@your_domain.com
region: your-ses-region
charset: UTF-8
```

### Create a class to manage SES
When you read through the SES docs about sending emails programmatically (you
did read them, right?) you probably noticed the `import boto3`  and botocore
lines. Since these are not part of the python standard library, you have to
install them.

Go ahead and add a line to your `requirements.txt` file:

```
boto3
```

Botocore will be taken care of as a dependency.

Next, make a new file `ses.py`. Within this file, add these imports to the top:
```
import os
import logging

import yaml
import boto3
from botocore.exceptions import ClientError
```

Then, make a line to connect to your app's logger so that if there is a problem,
we can log it:

```
logger = logging.getLogger('scaffold')
```

We'll use os to read the environment variables and open the config file, and
yaml to parse the config data. Create a class called `Ses`, and an `__init__`
method that accomplishes this:

```
class Ses():
    def __init__(self):
        """
        Reads the configuration details from the ses_config.yml file, and the
        credentials from env vars. Then instantiates a boto3 client for SES.
        """
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'ses_config.yml')) as infile:
                config = yaml.safe_load(infile)
                self.email = config['email']
                self.region = config['region']
                self.charset = config['charset']

                self.client = boto3.client(
                    'ses',
                    region_name=self.region,
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
                    aws_secret_access_key=os.environ['AWS_SECRET_KEY']
                )
                
        except Exception as e:
            logger.warning(f'SES failed due to {e}')
```

**WORKING HERE**

- add ContactForm to core/forms.py - (done needs docs)
- add import ContactForm to core/views.py - (done needs docs)
- add function contact to core/views.py - (WIP needs docs)
- add contact.html template - (not started)
