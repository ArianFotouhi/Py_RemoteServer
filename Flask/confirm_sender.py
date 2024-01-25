import io
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders



#########################stripe config#####################
import configparser
config = configparser.ConfigParser()
config.read('mysite/config/setting.ini')

sender_email_address = config['KEYS']['EMAIL_ADD']
sender_email_password = config['KEYS']['EMAIL_PASS']

###########################################################

def generate_invoice(customer_name, item_name, amount):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # Customize the invoice content here
    p.drawString(100, 750, f"Customer: {customer_name}")
    p.drawString(100, 730, f"Item: {item_name}")
    p.drawString(100, 710, f"Amount: ${amount}")
    # Add more details as needed

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

def send_invoice_email(customer_name, item_name, amount, customer_email):
    pdf_buffer = generate_invoice(customer_name, item_name, amount)

    # Set up your email configuration
    sender_email = sender_email_address  # replace with your email
    sender_password = sender_email_password  # replace with your email password
    smtp_server = "smtp.gmail.com"  # replace with your SMTP server

    subject = "Invoice"
    body = f"Hello {customer_name},\n\nThank you for your purchase. Please find the attached invoice for the item: {item_name}."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = customer_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    attachment = MIMEBase('application', 'pdf')
    attachment.set_payload(pdf_buffer.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename=invoice_{customer_name}.pdf')
    msg.attach(attachment)

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, customer_email, msg.as_string())
