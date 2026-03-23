# MARK: Imports

# python
import os
import smtplib
import ssl
from email.message import EmailMessage

#jc
import log_helper as logh
import generic_helper as genh


def send_email_notification(success: bool, recipients: list, subject: str, body: str):

    # Define server now so I can see it in the finally block
    server = None

    try:

        # Validate recipient list
        logh.log_entry(logh.SEPARATOR_3)
        logh.log_entry(f'Validating recipients list')

        if len(recipients) == 0:
            # must have at least one recipient
            logh.log_entry('No recipients specified.  Ending notification process.')
            return

        # Retrieve and validate SMTP details
        logh.log_entry(logh.SEPARATOR_3)
        logh.log_entry(f'Validating SMTP Connection Details...')

        env_server = os.getenv(genh.EnvVar.ITGEO_SMTP_SERVER.value, '')
        env_port = os.getenv(genh.EnvVar.ITGEO_SMTP_PORT.value, '-1')
        env_login = os.getenv(genh.EnvVar.ITGEO_SMTP_LOGIN.value, '')
        env_password = os.getenv(genh.EnvVar.ITGEO_SMTP_PASSWORD.value, '')
        env_sender = os.getenv(genh.EnvVar.ITGEO_SMTP_SENDER.value, '')

        if env_server == '' or env_port == -1 or env_login == '' or env_password == '' or env_sender == '':
            # Not enough info to send the email
            logh.log_entry('Insufficient SMTP information.  Ending notification process.')
            raise Exception('Insufficient SMTP information.') from None

        # Assemble the email subject
        subject_adjusted = ("SUCCESS" if success else "FAIL") + ' | ' + subject
        logh.log_entry(f'Email Subject: {subject_adjusted}')

        # Sender info
        sender_full = f'ITGeo Notification <{env_sender}>'
        logh.log_entry(f'Email Sender: {sender_full}')

        # Recipient Info
        recipients_concat = ','.join(recipients)
        logh.log_entry(f'Email Recipients: {recipients_concat}')

        # Construct the email body
        msg = EmailMessage()
        msg['From'] = sender_full
        msg['To'] = recipients_concat
        msg['Subject'] = subject_adjusted
        msg.set_content(body)

        # SEND THE EMAIL!

        # TODO: Re-enable SSL once certificate issue resolved
        # logh.log_entry('Creating SSL Context')
        # context = ssl.create_default_context()

        logh.log_entry('Creating SMTP Server Object...')
        server = smtplib.SMTP(env_server, int(env_port))

        # TODO: Re-enable SSL once certificate issue resolved
        # server.starttls(context=context)

        logh.log_entry(f'{logh.PFX1} Logging in...')
        server.login(user=env_login, password=env_password)

        logh.log_entry(f'{logh.PFX1} Sending message...')
        server.send_message(msg=msg, from_addr=env_sender, to_addrs=recipients)

    except Exception as ex:
        logh.log_entry(f'Error in "send_email_notification": {ex}')
    finally:
        # Close the SMTP server object
        if server is not None:
            server.quit()     
        logh.log_entry(f'Exiting send_email_notification function')
