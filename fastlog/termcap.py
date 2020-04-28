# Terminal features and colors
# Relies on a termcap database contained within the curses package
# pwnlib/term/termcap.py
import os

_win_compat = None

try:
    import curses
except ImportError:
    _win_compat = {
        "bold": {(): "\x1b\x5b\x31\x6d"},
        "setaf": {
            (1,): "\x1b\x5b\x33\x31\x6d",
            (2,): "\x1b\x5b\x33\x32\x6d",
            (3,): "\x1b\x5b\x33\x33\x6d",
            (4,): "\x1b\x5b\x33\x34\x6d",
            (5,): "\x1b\x5b\x33\x35\x6d",
            (7,): "\x1b\x5b\x33\x37\x6d",
        },
        "setab": {(1,): "\x1b\x5b\x34\x31\x6d"},
    }

_cache = {}


def get(cap, *args, **kwargs):
    """
    Get a terminal capability exposes through the `curses` module.
    """
    # Hack for readthedocs.org
    if "READTHEDOCS" in os.environ:
        return ""

    if _win_compat != None:
        print(cap, args)
        ret = _win_compat.get(cap).get(args)
        return ret

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
                    s = ""
                else:
                    s = bool(s)
        _cache[cap] = s

    # if 's' is not set 'curses.tparm' will throw an error if given arguments
    if args and s:
        r = curses.tparm(s, *args)
        return r.decode("utf-8")
    else:
        if isinstance(s, bytes):
            return s.decode("utf-8")
        else:
            return s
