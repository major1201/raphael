# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function
from email.mime.text import MIMEText
import smtplib


class MailSender:
    me = None
    password = None
    smtp_host = None
    port = None
    ssl = False

    def __init__(self, me, password, smtp_host, port=25, ssl=False):
        self.me = me
        self.password = password
        self.smtp_host = smtp_host
        self.port = port
        self.ssl = ssl

    def send_text_mail(self, subject, content, *to):
        msg = MIMEText(content, _subtype='plain', _charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = self.me
        msg['To'] = ';'.join(*to)
        try:
            if self.ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.port)
            server.login(self.me, self.password)
            server.sendmail(self.me, to, msg.as_string())
            server.close()
        except Exception as e:
            raise e
