import os
import smtplib
import subprocess
from os.path import basename
from datetime import date
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db.dal_connect import get_dal_mysql


SMTPSERVER = os.getenv("SMTPSERVER")
SMTPPORT = os.getenv("SMTPPORT")
SMTPUSER = os.getenv("SMTPUSER")
SMTPPASSWORD = os.getenv("SMTPPASSWORD")
FROMEMAIL = os.getenv("FROMEMAIL")
TOEMAIL = os.getenv("TOEMAIL")
FILEPATH = os.getenv("FILEPATH")


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

def send_email(date):
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
    files = ["relatorio", "login"]
    msg = MIMEMultipart()
    msg["From"] = FROMEMAIL
    msg["To"] = TOEMAIL
    msg["Subject"] = f"Relatório {date}"
    msg.attach(MIMEText(f"Relatório em anexo referente ao dia {date}", "plain"))

    for file in files:
        file_path = f"{FILEPATH}output/{file}_{date}.csv"
        with open(file_path, "rb") as file:
            part = MIMEApplication(file.read(), Name=basename(file_path))
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_path)
            msg.attach(part)

    try:
        server = smtplib.SMTP(SMTPSERVER, SMTPPORT)
        server.starttls()
        server.login(SMTPUSER, SMTPPASSWORD)

        text = msg.as_string()
        server.sendmail(FROMEMAIL, TOEMAIL, text)
        for file in files:
            file_path = f"{FILEPATH}output/{file}_{date}.csv"
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"- Failed to send email: {e}")
    finally:
        if server:
            try:
                server.quit()
            except Exception as e:
                print(f"Falha ao desconectar do servidor SMTP: {e}")
