import datetime
import logging.config
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml
from dotenv import dotenv_values

# import the customise logger YAML dictionary configuration file
# logging any error or any exception to a log file
with open(f'{os.path.abspath(".")}/config_log.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f.read())
    logging.config.dictConfig(yaml_config)

logger = logging.getLogger(__name__)


# load the .env values
env_config = dotenv_values(f"{os.path.abspath('.')}/.env")


def email_notification(msg, record_id):
    records = ''

    for sample_id in record_id:
        records += sample_id + '<br>'

    smtp_server = env_config['SMTP_SERVER']
    port = int(env_config['PORT'])
    sender_email = env_config['SENDER_EMAIL']
    password = env_config['PASSWORD']
    receiver_email = env_config['RECEIVER_EMAIL']

    message = MIMEMultipart('alternative')
    message['Subject'] = f'{datetime.date.today()} - New Records Imported into Laboratory Result REDCap Database'
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Cc'] = sender_email

    # Create the plain-text and HTML version of your message
    message_text = f"""\
    Hello,

    {msg}

    Below are the sample ids of the imported records:

    {records}

    REDCap Connector
    """
    message_html = f"""\
    <html>
        <body>
            <p>Hello,<br><br>
               <b>{msg}</b><br>
               Below are the sample ids of the imported records:<br><br>
               {records}<br><br><br>
               REDCap Connector
            </p>
        </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(message_text, "plain")
    part2 = MIMEText(message_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # can be omitted
        server.login(sender_email, password)
        # TODO: Send email here
        server.sendmail(sender_email, receiver_email, message.as_string())

    except Exception as e:
        logger.error(f'Error Occurred: {e}')

    if __name__ == '__main__':
        email_notification('test mic 1 2 1 2', [1, 2, 3, 4, 5])
