import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import qrcode
from reportlab.pdfgen import canvas

#########################stripe config#####################
import configparser
config = configparser.ConfigParser()
config.read('mysite/config/setting.ini')

sender_email_address = config['KEYS']['EMAIL_ADD']
sender_email_password = config['KEYS']['EMAIL_PASS']

###########################################################

def generate_qr_code_pdf(data):
    # Create QR code with larger size and less border
    qr = qrcode.QRCode(
        version=5,  # Increase version for larger size
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,  # Increase box size for larger QR code
        border=1,  # Decrease border for less border
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create a buffer to store the PDF
    buffer = io.BytesIO()

    # Create PDF with larger QR code
    c = canvas.Canvas(buffer)
    qr_img = qr.make_image(fill_color="black", back_color="white")


    c.drawInlineImage(qr_img, 120, 300, width=400, height=400)
    c.save()

    buffer.seek(0)
    return buffer

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
        <p>Please download the file due to expiration of the invoice link.</p>
        <hr>
        <h4>Lounge Atlas<h4>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = customer_email
    msg['Subject'] = subject

    # Attach HTML content
    msg.attach(MIMEText(body, 'html'))

    # Generate QR code as a PDF file
    qr_code_buffer = generate_qr_code_pdf('qrcode data')

    # Attach QR code as a PDF file
    qr_attachment = MIMEBase('application', 'pdf')
    qr_attachment.set_payload(qr_code_buffer.read())
    encoders.encode_base64(qr_attachment)
    qr_attachment.add_header('Content-Disposition', 'attachment; filename=QRcode.pdf')
    msg.attach(qr_attachment)

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, customer_email, msg.as_string())
