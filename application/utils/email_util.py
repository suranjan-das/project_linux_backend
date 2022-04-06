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
    <style>
        #userdeck {
          font-family: Arial, Helvetica, sans-serif;
          border-collapse: collapse;
          width: 100%;
        }

        #userdeck  td, #userdeck  th {
          border: 1px solid #ddd;
          padding: 8px;
        }

        #userdeck th {
          padding-top: 12px;
          padding-bottom: 12px;
          text-align: center;
          background-color: #04AA6D;
          color: white;
}
    </style>
</head>
<body>
<p>Dear {{data['name']}},</p>
<p>Welcome to our memory card application. Here is your monthly report. </p>
<p>Here are the actvities done by you in the last month</p>
<table id='userdeck'>
  <tr>
    <th>Deck Name</th>
    <th>Deck Info</th>
    <th>Last Viewed</th>
    <th>Deck Score</th>
  </tr>
  {% for deck in data.decks %}
  <tr>
    <td>{{ deck.deck_name }}</td>
    <td>{{ deck.deck_info }}</td>
    <td>{{ deck.time_viewed }}</td>
    <td>{{ deck.score }}</td>
  </tr>
  {% endfor %}
</table>
<p>If you have any query, Please contact us on flashcard@example.com.</p>
<p>Thank you for sticking with us</p>
<p>Regards, </p>
<p>Suranjan Das</p>
</body>
</html>'''

def format_message(template_file, data={}):
    template = Template(report_template)
    return template.render(data=data)

def send_welcome_message(data):
    message = format_message("monthly_report.html", data=data)
    status = send_email(data["email"], subject="Monthly review report", message=message, content="html", attachment_file=None)