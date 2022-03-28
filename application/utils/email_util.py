import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template

SMTP_SERVER_HOST = 'localhost'
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = 'myemail@example.com'
SENDER_PASSWORD = ''

def send_email(to_address, subject, message, content="text", attachment_file=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment_file:
        with open(attachment_file, 'rb') as attachment:
            # Add file as application/octet-stream
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        # Email attachment are sent as base64 encoded
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_file}",
            )
        # Add the attachment to tmsg
        msg.attach(part)

    # msg.attach(MIMEText(message, "html"))
    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    return True

report_template = '''<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title></title>
</head>
<body>
<p>Dear {{data['name']}},</p>
<p>Welcome to our learning application. We have attached the application guide for you. </p>
<p>If you have any query, Please contact us. </p>
<p>Regards, </p>
<p>Suranjan Das</p>
</body>
</html>'''

def format_message(template_file, data={}):
    # with open(template_file) as file_:
    #     template = Template(file_.read())
    #     return template.render(data=data)
    template = Template(report_template)
    return template.render(data=data)

def send_welcome_message(data):
    message = format_message("monthly_report.html", data=data)
    status = send_email(data["email"], subject="Welcome email", message=message, content="html", attachment_file=None)

# def main():
#     new_user = [
#         {"name": "Jolly", "email": "jolly@example.com"},
#         {"name": "Tuan", "email": "tuansona@example.com"}]

#     for user in new_user:
#         send_welcome_message(data=user)

# if __name__ == "__main__":
#     main()