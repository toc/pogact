#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import smtplib, ssl
from email.mime.text import MIMEText
import yaml


class MailReporter():
    """ Send report via Yahoo mail. """
    def __init__(self, config_file=None, mail_subject=None):
        """
        logging.SMTPHandler()の使用を前提に、初期設定のみ行う。
        """
        # ## set up logger
        # self.logger = logging.getLogger('MailReporter')
        # self.logger.setLevel(logging.INFO)

        ## read setting file.
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                conf = yaml.safe_load(f)
                mailhost = (
                    conf.get(r'smtphost', r'smtp.example.net'),
                    conf.get(r'smtpport', 25)
                )
                fromaddr = conf.get(r'fromaddr', r'noreply@example.net')
                toaddrs = conf.get(r'toaddrs', [r'noreply@example.net'])
                subject = mail_subject if type(mail_subject) is str \
                    else conf.get(r'subject', r'POGACT utils')
                credentials = (
                    conf.get(r'smtpacct', r'No_one'),
                    conf.get(r'smtppass', r'NoPassword')
                )
                secure = conf.get('secure',None)
                if secure == "TLS":
                    secure = ()

        except (TypeError, FileNotFoundError) as e:
            # Guess config_file is not correctly configured.
            print(f'{type(e)} {e.args}')
            raise FileNotFoundError(f'Does config_file exist? [{config_file}]')
        except Exception as e:
            #TODO: Destroy self.logger and set it to None.
            ex = Exception(f'Caught Exception: {type(e)} {e.args}.')
            raise ex

        ## set to instance variable
        self.mailhost = mailhost
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.credentials = credentials
        self.secure = secure
        self.server = None

        return

    def report(self, message):
    # def report(self, level, message):
        # if self.logger:
        #     if level == logging.FATAL:
        #         self.logger.critical(message)
        #     elif level == logging.ERROR:
        #         self.logger.error(message)
        #     elif level == logging.INFO:
        #         self.logger.info(message)
        #     elif level == logging.DEBUG:
        #         self.logger.debug(message)
        #     else:
        #         # Use warning if level is unknown value.
        #         self.logger.warning(message)
        print(message)
        self.send_message(message)
 
    def send_message(self, message):
        """
        """
        print(message)
        try:
            msg = MIMEText(message, "plain")
            msg["Subject"] = self.subject
            msg["From"] = self.fromaddr
            msg["To"] = ','.join(self.toaddrs)
            
            server = smtplib.SMTP_SSL(
                self.mailhost[0], # hostname
                self.mailhost[1], # port number
                context=ssl.create_default_context()
            )
            server.login(
                self.credentials[0],
                self.credentials[1]
            )
            server.send_message(msg)
            server.quit()
        except Exception as e:
            smtpex = smtplib.SMTPException(f'Caught Exception: {type(e)} {e.args}.')
            raise smtpex

    def setSubjectBase(self, subject):
        self.subject = subject

    # Obsolete
    def info(self, msg):
        self.report(msg)

    # Obsolete
    def critical(self, msg):
        self.report(msg)
