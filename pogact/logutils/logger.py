#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import inspect
from logging import Formatter, handlers, StreamHandler, getLogger, DEBUG
from pathlib import Path

# Reference: http://stackoverflow.com/questions/6810999/how-to-determine-file-function-and-line-number
# @return frameInfo
def frameinfo(stackIndex=3):
    stacks = inspect.stack()
    stack_count = len(stacks)
    if stackIndex > 0:
        # Pick up stack from FIRST of array(=nearest call) if stackIndex > 0
        if stackIndex >= stack_count:
            return None
    else:
        # Pick up stack from LAST of array(=farest call) or 0 if stackIndex <= 0
        stackIndex = stack_count + stackIndex
        if stackIndex < 0:
            return None
    callerframerecord = stacks[stackIndex]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return info


class Logger:
    def __init__(self, name=__name__, clevel=None, flevel=None, annotate=True,path=None):
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
        if path != None:
            path = Path(path) if type(path) is str else path
        path.mkdir(parents=True,exist_ok=True)
        logfile = path / f"{name}.log"
        level = DEBUG if flevel is None else flevel
        handler = handlers.RotatingFileHandler(
            filename = str(logfile), encoding=r'utf-8',
            maxBytes = 1048576, backupCount = 3
        )
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
