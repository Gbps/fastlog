# Terminal features and colors
# Relies on a termcap database contained within the curses package
# pwnlib/term/termcap.py
import curses
import os

_cache = {}

def get(cap, *args, **kwargs):
    """
    Get a terminal capability exposes through the `curses` module.
    """
    # Hack for readthedocs.org
    if 'READTHEDOCS' in os.environ:
        return ''

    if kwargs != {}:
        raise TypeError("get(): No such argument %r" % kwargs.popitem()[0])

    if _cache == {}:
        # Fix for BPython
        try:
            curses.setupterm()
        except:
            pass
    
    s = _cache.get(cap)
    if not s:
        s = curses.tigetstr(cap)
        if s == None:
            s = curses.tigetnum(cap)
            if s == -2:
                s = curses.tigetflag(cap)
                if s == -1:
                    # default to empty string so tparm doesn't fail
                    s = ''
                else:
                    s = bool(s)
        _cache[cap] = s

    # if 's' is not set 'curses.tparm' will throw an error if given arguments
    if args and s:
        r = curses.tparm(s, *args)
        return r.decode('utf-8')
    else:
        if isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            return s
