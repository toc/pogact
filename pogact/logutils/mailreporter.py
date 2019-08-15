#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from logging.handlers import SMTPHandler
import yaml


class MailReporter():
    """ Send report via Yahoo mail. """
    def __init__(self):
        self.logger = logging.getLogger('MailReporter')
        self.logger.setLevel(logging.INFO)

    def setup(self, config_file, mail_subject=None):
        result = r''
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
                    else conf.get(r'subject', r'RWebSearch auto')
                credentials = (
                    conf.get(r'smtpacct', r'No_one'),
                    conf.get(r'amtppass', r'NoPassword')
                )
                secure = None
            handler = SMTPHandler(mailhost, fromaddr, toaddrs, subject, credentials, secure)
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
        except Exception as e:
            result = f'Caught Exception: {type(e)}.'
            #TODO: Destroy self.logger and set it to None.

        return result

    def report(self, msg):
        if self.logger:
            self.logger.critical(msg)

    def info(self, msg):
        if self.logger:
            self.logger.info(msg)

    def critical(self, msg):
        if self.logger:
            self.logger.critical(msg)
