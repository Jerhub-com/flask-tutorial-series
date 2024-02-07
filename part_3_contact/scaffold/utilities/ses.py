import os
import logging

import yaml
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger('scaffold')


class Ses():
    """
    Configures Amazon Simple Email Service (SES) for sending emails.

    Adapted from the AWS documentation at:
    https://docs.aws.amazon.com/ses/latest/dg/send-an-email-using-sdk-programmatically.html

    Configuration must be setup as follows prior to instantiating this class:
        - 'AWS_ACCESS_KEY' should be set as an environment variable.
        - 'AWS_SECRET_KEY' should be set as an environment variable.
        - email, region, and charset should be set in the 'ses_config.yml' file
          located in this directory.
    
    Example Usage:
        from scaffold.utilities.ses import Ses

        ses = Ses()
        ses.send_email(subject='hello',
                       body_html='<p>Hello!</p>',
                       client_address='bob@example.com',
                       )

    """
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

    def send_email(self, subject, body, body_html, client_address) -> bool:
        """
        Sends an email using the boto3 client and the provided details.

        Example:
            ses.send_email(subject='hello',
                       body='Hello!',
                       body_html='<p>Hello!</p>',
                       client_address='bob@example.com',
                       )
        """
        success = False

        try:
            response = self.client.send_email(
                Destination={
                    'ToAddresses': [client_address,],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': self.charset,
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': self.charset,
                            'Data': body,
                        },
                    },
                    'Subject': {
                        'Charset': self.charset,
                        'Data': subject,
                    },
                },
                Source=self.email,
            )

        except ClientError as e:
            logger.warning(e.response['Error']['Message'])

        else:
            logger.warning(f'Email sent. Message ID: {response["MessageId"]}')
            success = True

        return success
