#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import inspect
from logging import Formatter, handlers, StreamHandler, getLogger, DEBUG


# Reference: http://stackoverflow.com/questions/6810999/how-to-determine-file-function-and-line-number
# @return frameInfo
def frameinfo(stackIndex=3):
    stack = inspect.stack()
    if stackIndex >= len(stack):
        return None
    callerframerecord = stack[stackIndex]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return info


class Logger:
    def __init__(self, name=__name__, clevel=None, flevel=None, annotate=True):
        self.logger = getLogger(name)
        self.logger.setLevel(DEBUG)
        self.annotate = annotate
        formatter = Formatter("[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s] %(message)s")

        # stdout
        level = DEBUG if clevel is None else clevel
        handler = StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # file
        level = DEBUG if flevel is None else flevel
        handler = handlers.RotatingFileHandler(filename = f"{name}.log",
                                               maxBytes = 1048576,
                                               backupCount = 3)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def add_annotation(self, orig_msg):
        msg = str(orig_msg)
        if self.annotate is True:
            info = frameinfo()
            if info is not None:
                msg += f" [{os.path.basename(info.filename)}@{str(info.lineno)}]"
            else:
                msg += f" [failed inspection]"
        return msg

    def debug(self, msg):
        self.logger.debug(f"{self.add_annotation(msg)}")

    def info(self, msg):
        self.logger.info(f"{self.add_annotation(msg)}")

    def warn(self, msg):
        self.logger.warn(f"{self.add_annotation(msg)}")

    def error(self, msg):
        self.logger.error(f"{self.add_annotation(msg)}")

    def critical(self, msg):
        self.logger.critical(f"{self.add_annotation(msg)}")
