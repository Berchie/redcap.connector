import datetime
import logging.config
import os
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import dotenv_values, load_dotenv
from loguru import logger
from redcapconnector.config.log_config import handlers


# setting up the logging
logger.configure(
    handlers=handlers,
)

# load the .env values(development)
env_config = dotenv_values("../.env")

# load .env variables(prod)
dotenv_path = os.path.abspath(f"{os.environ['HOME']}/.env")
if os.path.abspath(f"{os.environ['HOME']}/.env"):
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise logger.exception('Could not found the application environment variables!')


def email_notification(msg, record_id):
    records = ''

    for sample_id in record_id:
        records += sample_id + '<br>'

    smtp_server = os.environ['SMTP_SERVER']
    port = int(os.environ['PORT'])
    sender_email = os.environ['SENDER_EMAIL']
    password = os.environ['PASSWORD']
    receiver_email = [os.environ['RECEIVER_EMAIL'], os.environ['CC_EMAIL']]
    # cc_email = env_config['CC_EMAIL']

    message = MIMEMultipart('alternative')
    message['Subject'] = f'{datetime.date.today()} - New Records Imported into Laboratory Result REDCap Database'
    message['From'] = sender_email
    message['To'] = ','.join(receiver_email)
    # message['Cc'] = cc_email

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
               <b>{msg}</b><br><br>
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
        logger.exception(f'Error Occurred: {e}')


if __name__ == '__main__':
    email_notification('test mic 1 2 1 2', [1, 2, 3, 4, 5])
