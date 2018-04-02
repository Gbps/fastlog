# Escapes for colors and formatting

from . import termcap
from . import styles
import six

def numcolors():
    """
    Returns the number of colors this terminal supports
    """
    try:
        clrs = termcap.get('colors') or 8
    except Exception:
        clrs = 8
    
    return clrs

def hasbright():
    """
    Returns True if the terminal supports bright colors
    """
    return numcolors() >= 16

colorcodes = {
    'black': 0,
    'red': 1,
    'green': 2,
    'yellow': 3,
    'blue': 4,
    'magenta': 5,
    'cyan': 6,
    'white': 7,
    'gray': -1,
    'grey': -1,
}

# Default to using 'bright' colors if terminal supports it
# If the terminal supports grey, replace -1 with 'bright black', 8
# https://upload.wikimedia.org/wikipedia/commons/1/15/Xterm_256color_chart.svg
if hasbright():
    colorcodes = {
        'black': 0,
        'red': 9,
        'green': 10,
        'yellow': 11,
        'blue': 12,
        'magenta': 13,
        'cyan': 14,
        'white': 15,
        'gray': 8,
        'grey': 8,
    }

fmttypes = {
    # Italics
    'i': 'sitm',
    # Bold
    'b': 'bold',
    # Underline
    'u': 'smul',
    # Reverse
    'r': 'rev',
    }

class Style(object):
    def __init__(self, descriptor):
        """
        Initializes a style object. See `parse`
        """
        self.parse(descriptor)
    
    def __call__(self, msg):
        """
        Formats a message with this style by calling the underlying decorator
        """
        return self.decorator(msg)

    def parse(self, descriptor):
        """
        Creates a text styling from a descriptor

        A descriptor is a dictionary containing any of the following keys:
            * fg: The foreground color (name or int)
                    See `bgseq`
            * bg: The background color (name or int)
                    See `fgseq`
            * fmt: The types of special text formatting (any combination of 'b', 'u', 'i', and 'r')
                    See `typeseq`
        """
        fg = descriptor.get('fg')
        bg = descriptor.get('bg')
        types = descriptor.get('fmt')
        ret = ""
        if fg:
            ret += fgseq(fg)
        if bg:
            ret += bgseq(bg)
        if types:
            t = typeseq(types)
            if t:
                ret += t
        
        # wew, strings and bytes, what's a guy to do!
        reset = resetseq()
        if not isinstance(reset, six.text_type):
            reset = reset.decode('utf-8')
        
        def ret_func(msg):
            if not isinstance(msg, six.text_type):
                msg = msg.decode('utf-8')
            return ret + msg + reset

        self.decorator = ret_func



def typeseq(types):
    """
    Returns an escape for a terminal text formatting type, or a list of types.

    Valid types are:
        * 'i' for 'italic'
        * 'b' for 'bold'
        * 'u' for 'underline'
        * 'r' for 'reverse'
    """
    ret = ""
    for t in types:
        ret += termcap.get(fmttypes[t])
    
    return ret

def nametonum(name):
    """
    Returns a color code number given the color name.
    """
    code = colorcodes.get(name)
    if code is None:
        raise ValueError("%s is not a valid color name." % name)
    else:
        return code

def fgseq(code):
    """
    Returns the forground color terminal escape sequence for the given color code number or color name.
    """
    if isinstance(code, str):
        code = nametonum(code)
    
    if code == -1:
        return ""
    
    s = termcap.get('setaf', code) or termcap.get('setf', code)
    return s

def bgseq(code):
    """
    Returns the background color terminal escape sequence for the given color code number.
    """
    if isinstance(code, str):
        code = nametonum(code)

    if code == -1:
        return ""

    s = termcap.get('setab', code) or termcap.get('setb', code)
    return s

def resetseq():
    """
    Returns the reset terminal escape sequence
    """
    return '\x1b[m'


