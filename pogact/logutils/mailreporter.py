#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from logging.handlers import SMTPHandler
import yaml


class MailReporter():
    """ Send report via Yahoo mail. """
    def __init__(self, config_file=None, mail_subject=None):
        self.logger = logging.getLogger('MailReporter')
        self.logger.setLevel(logging.INFO)

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
                    conf.get(r'smtppass', r'NoPassword')
                )
                secure = None
            handler = SMTPHandler(mailhost, fromaddr, toaddrs, subject, credentials, secure)
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
        except (TypeError, FileNotFoundError) as e:
            # Guess config_file is not correctly configured.
            print(f'{type(e)} {e.args}')
            raise FileNotFoundError(f'Does config_file exist? [{config_file}]')
        except Exception as e:
            #TODO: Destroy self.logger and set it to None.
            result = f'Caught Exception: {type(e)} {e.args}.'
            raise e

        return

    def report(self, msg):
        if self.logger:
            self.logger.critical(msg)

    def info(self, msg):
        if self.logger:
            self.logger.info(msg)

    def critical(self, msg):
        if self.logger:
            self.logger.critical(msg)
