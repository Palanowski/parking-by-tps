import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db.dal_connect import get_dal_mysql


SMTPSERVER = os.getenv("SMTPSERVER")
SMTPPORT = os.getenv("SMTPPORT")
SMTPUSER = os.getenv("SMTPUSER")
SMTPPASSWORD = os.getenv("SMTPPASSWORD")
FROMEMAIL = os.getenv("FROMEMAIL")
TOEMAIL = os.getenv("TOEMAIL")


def get_config():
    with get_dal_mysql() as db:
        config = db().select(db.config.ALL)
    return config.as_dict()[1]


def update_config(tolerance: int = None, header: str = None, footer: str = None):
    with get_dal_mysql() as db:
        if tolerance:
            db(db.config.id==1).update(tolerance=tolerance)
        if header:
            db(db.config.id==1).update(printer_header=header)
        if footer:
            db(db.config.id==1).update(printer_footer=footer)
    return True

def send_email(from_email, to_email, subject, body):
    """
    This function sends an email using the specified parameters.

    Args:
        from_email (str): The sender's email address.
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body text of the email.

    Returns:
        None
    """
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTPSERVER, SMTPPORT)
        server.starttls()
        server.login(SMTPUSER, SMTPPASSWORD)

        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
    except Exception as e:
        print(f"- Failed to send email: {e}")
    finally:
        if server:
            try:
                server.quit()
            except Exception as e:
                print(f"Falha ao desconectar do servidor SMTP: {e}")