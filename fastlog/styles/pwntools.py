from ..term import Style

"""
Characters used for identation
"""
indent = '    '

"""
The prefixes dictionary sets all of the styles for log messages based
on the type of log (eg. log.info)

An entry in the prefix list must provide a key for each type of message:
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

A prefix contains the text formatting for the output between the [] brackets of the logger.

The value of the key will be a list of format [Style, str] where the Style
dictates the colors and styles of the str as it is printed out as a prefix.

When a log entry is being formatted, a lookup is performed on the prefixes directory for the current style.
When the key is found, the Style object will generate ANSI escapes which will style the prefix character that follows.

If the logger is outputting to a non-tty (eg. a file), the Style object will not be used and
the str for the given entry will be printed out as normal characters.

Example:
"[*] Info"
    * The '*' is dictated by second element of the 'info' prefix below
    * The '*' is colored blue by the 'fg': 'blue' entry in the Style, and bolded by the 'fmt': 'b' entry

"""
prefixes = {
    'status'       : [Style({'fg': 'magenta'}), 'x'],
    'success'      : [Style({'fmt': 'b', 'fg': 'green'}), '+'],
    'failure'      : [Style({'fmt': 'b', 'fg': 'red'}), '-'],
    'debug'        : [Style({'fmt': 'b', 'fg': 'red'}), 'DEBUG'],
    'info'         : [Style({'fmt': 'b', 'fg': 'blue'}), '*'],
    'warning'      : [Style({'fmt': 'b', 'fg': 'yellow'}), '!'],
    'error'        : [Style({'fg': 'white', 'bg': 'red'}), 'ERROR'],
    'exception'    : [Style({'fg': 'white', 'bg': 'red'}), 'ERROR'],
    'critical'     : [Style({'fg': 'white', 'bg': 'red'}), 'CRITICAL'],
    'info_once'    : [Style({'fmt': 'b', 'fg': 'blue'}), '*'],
    'warning_once' : [Style({'fmt': 'b', 'fg': 'yellow'}), '!']
    }

"""
The `separator` variable defines the style of the separator when called with `log.separator()`.

The first element of the list is the style of text as it's printed

The second element of the list is the characters to print out for the separator
"""
separator = [ Style({'fg': 'gray'}), '-'*87 ]

"""
The `hexdump` variable defines the style of the hexdump output.

This is a dictionary of hex/special names and the styles they map to.

The special style names are:
    * marker - The style of the | markers
    * printable - The style of printable ASCII bytes
    * nonprintable - The style of the nonprintable ASCII bytes
    * highlight - The style of hex characters when passed the highlight kwarg to hexdump
"""
hexdump = {
    'marker':       Style({'fg': 'gray'}),
    'printable':    Style({}),
    'nonprintable': Style({'fg': 'gray'}),
    'highlight':    Style({'fg': 'white', 'bg': 'red'}),
    '00':           Style({'fg': 'red'}),
    '0a':           Style({'fg': 'red'}),
    'ff':           Style({'fg': 'green'}),
}
