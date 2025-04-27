import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging

class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password, sender_name="AI节日邮件", ssl=True):
        """初始化邮件发送器，设置SMTP服务器详细信息。

        参数:
            smtp_server (str): SMTP服务器地址
            smtp_port (int): SMTP服务器端口
            username (str): SMTP用户名
            password (str): SMTP密码
            sender_name (str): 显示的发件人名称
            ssl (bool): 是否使用SSL连接，默认为True
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_name = sender_name
        self.use_ssl = ssl

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

    def send_email(self, recipients, subject, body):
        """向指定收件人发送邮件。

        参数:
            recipients (list): 收件人邮箱地址列表
            subject (str): 邮件主题
            body (str): 邮件正文（HTML格式）

        返回:
            bool: 发送成功返回True，否则返回False
        """
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
        self.logger.info(f"正在连接SMTP服务器 {self.smtp_server}:{self.smtp_port}...")
        try:
            if self.use_ssl:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    self.logger.info("使用SSL连接SMTP服务器成功，正在进行身份验证...")
                    server.login(self.username, self.password)
                    self.logger.info("身份验证成功，开始发送邮件...")
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    self.logger.info("使用非SSL连接SMTP服务器成功，正在进行身份验证...")
                    server.starttls()  # 启用TLS加密
                    server.login(self.username, self.password)
                    self.logger.info("身份验证成功，开始发送邮件...")

                for recipient in recipients:
                    msg['To'] = recipient
                    try:
                        server.sendmail(self.username, recipient, msg.as_string())
                        self.logger.info(f"邮件已成功发送至 {recipient}")
                    except smtplib.SMTPException as se:
                        self.logger.error(f"发送邮件至 {recipient} 时出错：{str(se)}")
                        raise

            self.logger.info("所有邮件发送完成")
            return True

        except smtplib.SMTPConnectError as ce:
            self.logger.error(f"连接SMTP服务器失败：{str(ce)}")
            self.logger.info("请检查：1. SMTP服务器地址和端口是否正确 2. 网络连接是否正常 3. 防火墙设置是否允许连接")
            return False
        except smtplib.SMTPAuthenticationError as ae:
            self.logger.error(f"SMTP身份验证失败：{str(ae)}")
            self.logger.info("请检查：1. 用户名是否正确 2. 密码是否正确（如果使用的是邮箱的授权码，请确保授权码有效）")
            return False
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP操作失败：{str(e)}")
            self.logger.info("请检查SMTP服务器配置和网络连接状态")
            return False
        except Exception as e:
            self.logger.error(f"发送邮件时发生未知错误：{str(e)}")
            return False
