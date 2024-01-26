import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#########################stripe config#####################
import configparser
config = configparser.ConfigParser()
config.read('mysite/config/setting.ini')

sender_email_address = config['KEYS']['EMAIL_ADD']
sender_email_password = config['KEYS']['EMAIL_PASS']

###########################################################


def send_invoice_email(customer_name, item_name, amount, customer_email, pdf_link):

    # Set up your email configuration
    sender_email = sender_email_address  # replace with your email
    sender_password = sender_email_password  # replace with your email password
    smtp_server = "smtp.gmail.com"  # replace with your SMTP server


    subject = "Lounge Atlas purchase invoice"

    body = f"""
        <p>Hello {customer_name},</p>
        <p>Thank you for your purchase. Please find the invoice for the item: {item_name} by clicking the link below:</p>
        <p><a href="{pdf_link}">View Invoice</a></p>
        <p>Please download the file due to expiration of invoice link.</p>
        <hr>
        <h4>Lounge Atlas<h4>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = customer_email
    msg['Subject'] = subject

    # Attach HTML content
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, customer_email, msg.as_string())
