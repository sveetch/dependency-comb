import logging

import colorlog

from ..exceptions import DependencyCombError
from .. import __pkgname__


def init_logger(name, level, printout=True):
    """
    Initialize app logger to configure its level/handler/formatter/etc..

    Arguments:
        name (str): Logger name used to instanciate and retrieve it.
        level (str): Level name (``debug``, ``info``, etc..) to enable.

    Keyword Arguments:
        printout (bool): If False, logs will never be outputed.

    Returns:
        logging.Logger: Application logger.
    """
    root_logger = logging.getLogger(name)
    root_logger.setLevel(level)

    # Redirect outputs to the void space, mostly for usage within unittests
    if not printout:
        from io import StringIO
        dummystream = StringIO()
        handler = logging.StreamHandler(dummystream)
    # Standard output with colored messages
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(asctime)s - %(log_color)s%(message)s",
                datefmt="%H:%M:%S"
            )
        )

    root_logger.addHandler(handler)

    return root_logger


class NoOperationLogger:
    """
    A fake logger which don't do anything, given messages to logging method just fall
    into void except for ``critical`` which raise the ``DependencyCombError`` exception.
    """
    def __init__(self, *args, **kwargs):
        pass

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def critical(self, msg):
        raise DependencyCombError(msg)


class LoggerBase:
    """
    A basic class just to ship the required logger object.

    This class should be at the last position in inheritance definition, since it must
    be called first because next classes may require its ``self.log`` attribute.
    """
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__pkgname__)
