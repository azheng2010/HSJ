#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging, os, sys, time
class logger:
    def __init__(self, set_level='debug', name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1], log_name=time.strftime('%Y-%m-%d_%H_%M_%S.log', time.localtime()), log_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log'), use_console=False):
        self.logger = logging.getLogger(name)
        if set_level.lower() == 'critical':
            self.logger.setLevel(logging.CRITICAL)
        else:
            if set_level.lower() == 'error':
                self.logger.setLevel(logging.ERROR)
            else:
                if set_level.lower() == 'warning':
                    self.logger.setLevel(logging.WARNING)
                else:
                    if set_level.lower() == 'info':
                        self.logger.setLevel(logging.INFO)
                    else:
                        if set_level.lower() == 'debug':
                            self.logger.setLevel(logging.DEBUG)
                        else:
                            self.logger.setLevel(logging.NOTSET)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_file_path = os.path.join(log_path, log_name)
        self.log_file_path = log_file_path
        log_handler = logging.FileHandler(log_file_path,encoding='utf-8')
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n' + '-' * 30))
        self.logger.addHandler(log_handler)
        if use_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(console_handler)
    def addHandler(self, hdlr):
        self.logger.addHandler(hdlr)
    def removeHandler(self, hdlr):
        self.logger.removeHandler(hdlr)
    def critical(self, msg, *args, **kwargs):
        if not msg.startswith('\n'):
            msg = '\n' + msg
        try:
            self.logger.critical(msg, *args, **kwargs)
        except:
            pass
    def warning(self, msg, *args, **kwargs):
        if not msg.startswith('\n'):
            msg = '\n' + msg
        try:
            self.logger.warning(msg, *args, **kwargs)
        except:
            pass
    def error(self, msg, *args, **kwargs):
        if not msg.startswith('\n'):
            msg = '\n' + msg
        try:
            self.logger.error(msg, *args, **kwargs)
        except:
            pass
    def info(self, msg, *args, **kwargs):
        if not msg.startswith('\n'):
            msg = '\n' + msg
        try:
            self.logger.info(msg, *args, **kwargs)
        except:
            pass
    def debug(self, msg, *args, **kwargs):
        if not msg.startswith('\n'):
            msg = '\n' + msg
        try:
            self.logger.debug(msg, *args, **kwargs)
        except:
            pass
    def log(self, level, msg, *args, **kwargs):
        if not msg.startswith('\n'):
            msg = '\n' + msg
        try:
            self.logger.log(level, msg, *args, **kwargs)
        except:
            pass
if __name__ == '__main__':
    pass