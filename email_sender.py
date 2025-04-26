import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging

class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password, sender_name="AI节日邮件"):
        """初始化邮件发送器，设置SMTP服务器详细信息。

        参数:
            smtp_server (str): SMTP服务器地址
            smtp_port (int): SMTP服务器端口
            username (str): SMTP用户名
            password (str): SMTP密码
            sender_name (str): 显示的发件人名称
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_name = sender_name

        # 设置日志记录
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
        """向指定收件人发送邮件。

        参数:
            recipients (list): 收件人邮箱地址列表
            subject (str): 邮件主题
            body (str): 邮件正文（HTML格式）
            poster_path (str, optional): 海报图片路径（可选）

        返回:
            bool: 发送成功返回True，否则返回False
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr((self.sender_name, self.username))
            msg['Subject'] = subject

            # 添加HTML正文
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

            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)

                for recipient in recipients:
                    msg['To'] = recipient
                    server.sendmail(self.username, recipient, msg.as_string())
                    self.logger.info(f"邮件已发送至 {recipient}")

            return True

        except Exception as e:
            self.logger.error(f"邮件发送失败：{str(e)}")
            return False
