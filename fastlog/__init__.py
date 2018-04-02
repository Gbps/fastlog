from . import term
from . import log as _log

"""
Import the log object into your project to use fastlog

This can be done simply by using:
>>> from fastlog import log
or
>>> from fastlog import *

"""
log = _log.FastLogger()