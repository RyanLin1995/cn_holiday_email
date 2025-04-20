import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging

class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password, sender_name="AI节日邮件"):
        """Initialize the EmailSender with SMTP server details.

        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port
            username (str): SMTP username
            password (str): SMTP password
            sender_name (str): Sender name to display in emails
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_name = sender_name

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("email_sender.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("EmailSender")

    def send_email(self, recipients, subject, body, poster_path=None):
        """Send an email to the specified recipients.

        Args:
            recipients (list): List of recipient email addresses
            subject (str): Email subject
            body (str): Email body (HTML format)
            poster_path (str, optional): Path to the poster image to attach

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr((self.sender_name, self.username))
            msg['Subject'] = subject

            # Add HTML body
            # 预处理需要替换的内容
            body_html = body.replace('\n', '<br>')

            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    {body_html}

                    <div class="footer">
                        <p>此邮件由公司文化部发送</p>
                        <p>如有疑问，请联系文化部：culture@company.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, 'html'))

            # 海报功能已移除
            # 忽略poster_path参数

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)

                for recipient in recipients:
                    msg['To'] = recipient
                    server.sendmail(self.username, recipient, msg.as_string())
                    self.logger.info(f"Email sent to {recipient}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False
