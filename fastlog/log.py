import logging
import importlib
import sys
import six
from . import hexdump
class FastLogger:
    """
    fastlog provides a simple, clean logging interface for your Python scripts
    """

    def __init__(self):
        # Only one top-level logger, for simplicity
        self.inner = logging.getLogger("fastlog")
        
        # Setup in setStyle
        self._handlers = []

        # Default style
        self.setStyle("fastlog.styles.pwntools")

        # Default level
        self.setLevel(logging.INFO)

        # Initial no indent
        self._indent = 0

        # Last level for functions that default to the last print message level
        self._lastlevel = logging.INFO

        # Logger defines for ease of use
        self.INFO = logging.INFO
        self.DEBUG = logging.DEBUG
        self.CRITICAL = logging.CRITICAL
        self.ERROR = logging.ERROR
        self.WARNING = logging.WARNING
        self.NOTSET = logging.NOTSET

    def addHandler(self, handler):
        """
        Setups a new internal logging handler. For fastlog loggers,
        handlers are kept track of in the self._handlers list
        """
        self._handlers.append(handler)
        self.inner.addHandler(handler)
    
    def setStyle(self, stylename):
        """
        Adjusts the output format of messages based on the style name provided

        Styles are loaded like python modules, so you can import styles from your own modules or use the ones in fastlog.styles

        Available styles can be found under /fastlog/styles/

        The default style is 'fastlog.styles.pwntools'
        """
        self.style = importlib.import_module(stylename)
        newHandler = Handler()
        newHandler.setFormatter(Formatter(self.style))
        self.addHandler(newHandler)

    def setLevel(self, level):
        """
        Sets the threshold for this handler to level. Logging messages which are less severe than level will be ignored.
        """
        self.inner.setLevel(level)
    
    def _log(self, lvl, msg, type, args, kwargs):
        """
        Internal method to filter into the formatter before being passed to the main Python logger
        """
        extra = kwargs.get('extra', {})
        extra.setdefault("fastlog-type", type)
        extra.setdefault("fastlog-indent", self._indent)
        kwargs['extra'] = extra

        self._lastlevel = lvl

        self.inner.log(lvl, msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self._log(self.INFO, msg, 'info', args, kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(self.DEBUG, msg, 'debug', args, kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(self.WARNING, msg, 'warning', args, kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self._log(self.CRITICAL, msg, 'critical', args, kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(self.ERROR, msg, 'error', args, kwargs)

    def success(self, msg, *args, **kwargs):
        self._log(self.INFO, msg, 'success', args, kwargs)
    
    def failure(self, msg, *args, **kwargs):
        self._log(self.INFO, msg, 'failure', args, kwargs)
    
    def exception(self, msg, *args, **kwargs):
        #kwargs["exc_info"] = 1
        self._log(self.ERROR, msg, 'exception', args, kwargs)
        raise Exception(msg % args)
    
    def separator(self, *args, **kwargs):
        """
        Prints a separator to the log. This can be used to separate blocks of log messages.

        The separator will default its log level to the level of the last message printed unless
        specified with the level= kwarg.

        The length and type of the separator string is determined
        by the current style. See ``setStyle``
        """
        levelOverride = kwargs.get('level') or self._lastlevel
        self._log(levelOverride, '', 'separator', args, kwargs)
    
    def indent(self):
        """
        Begins an indented block. Must be used in a 'with' code block.
        All calls to the logger inside of the block will be indented.
        """
        blk = IndentBlock(self, self._indent)
        self._indent += 1
        return blk
    
    def setIndent(self, indent):
        """
        Sets the current indentation level
        """
        if indent >= 0:
            self._indent = indent

    def newline(self, *args, **kwargs):
        """
        Prints an empty line to the log. Uses the level of the last message
        printed unless specified otherwise with the level= kwarg.
        """
        levelOverride = kwargs.get('level') or self._lastlevel
        self._log(levelOverride, '', 'newline', args, kwargs)

    def hexdump(self, s, *args, **kwargs):
        """
        Outputs a colorful hexdump of the first argument. 

        This function will attempt to 'flatten' iterable data passed to it until all remaining elements
        are binary representable.

        In python2, objects should be of type 'str', in python3, 'bytes' or 'bytearray' will work.

        The level of the last message printed is used unless specified otherwise with the level= kwarg

        Arguments to pass to hexdump:
            width(int): The number of characters per line
            skip(bool): Set to True, if repeated lines should be replaced by a "*"
            hexii(bool): Set to True, if a hexii-dump should be returned instead of a hexdump.
            begin(int):  Offset of the first byte to print in the left column
            highlight(iterable): Byte values to highlight.
        """
        levelOverride = kwargs.get('level') or self._lastlevel
        hexdmp = hexdump.hexdump(self, s, **kwargs)
        self._log(levelOverride, hexdmp, 'indented', args, kwargs)

class IndentBlock(object):
    """
    Allows the usage of the python 'with' keyword to provide blocks of
    indented logs.

    Example:

    with log.indent():
        log.info("Indented!")
    """

    def __init__(self, parent, oldIndentLevel):
        self.parent = parent
        self.old = oldIndentLevel
    
    def __enter__(self):
        return self

    def __exit__(self, exc_typ, exc_val, exc_tb):
        self.parent.setIndent(self.old)

class Formatter(logging.Formatter):
    """
    Logging formatter which performs custom formatting for log records
    containing the ``fastlog-type`` attribute.

    Valid attributes passed to the style are:
        * status
        * success
        * failure
        * debug
        * info
        * warning
        * error
        * exception
        * critical
        * info_once
        * warning_once
        * animated
        * separator
        * newline
        * indented
    """

    # Indentation from the left side of the terminal.
    # All log messages will be indented at list this far.
    indent    = '    '

    # Newline, followed by an indent.  Used to wrap multiple lines.
    nlindent  = '\n' + indent

    def __init__(self, style, *args, **kwargs):
        super(Formatter, self).__init__(*args, **kwargs)
        self.style = style
        self.indent = self.style.indent
        self.nlindent = '\n' + self.indent

    def format(self, record):
        # use the default formatter to actually format the record
        msg = super(Formatter, self).format(record)

        # then put on a prefix symbol according to the message type
        msgtype = getattr(record, 'fastlog-type', None)
        
        # Number of indents to the prefix
        indentLevel = getattr(record, 'fastlog-indent', None)
        
        # if 'fastlog-type' is not set (or set to `None`) we just return the
        # message as it is
        if msgtype is None:
            return msg

        prefix = self.indent*indentLevel

        if msgtype == 'separator':
            stylefunc, symb = self.style.separator
            msg = stylefunc(symb)
        elif msgtype == 'newline':
            msg = ''
            prefix = ''
        elif msgtype == 'animated':
            # the handler will take care of updating the spinner, so we will
            # not include it here
            prefix = ''
        elif msgtype == 'indented':
            prefix = self.indent
        elif msgtype in self.style.prefixes:
            # Execute the prefix style function if the prefix exists
            stylefunc, symb = self.style.prefixes[msgtype]
            prefix += '[%s] ' % stylefunc(symb)
        else:
            # No valid prefix was found, fallback on a default
            prefix += '[?] '

        msg = prefix + msg
        msg = self.nlindent.join(msg.splitlines())
        return msg

class Handler(logging.StreamHandler):
    """
    An instance of a fastlog handler
    """
    @property
    def stream(self):
        return sys.stdout
    
    @stream.setter
    def stream(self, value):
        pass