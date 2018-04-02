# -*- coding: utf-8 -*-
# From pwntool's pwnlib, modified for py3 and fastlog
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import string
import struct
import six

def _flat(args):
    out = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            out.append(_flat(arg))
        elif isinstance(arg, str):
            out.append(arg)
        elif isinstance(arg, unicode):
            out.append(arg.encode('utf8'))
        # Not supporting integer packing for now
        #elif isinstance(arg, (int, long)):
            #out.append(struct.pack("<Larg))
        elif isinstance(arg, bytearray):
            out.append(str(arg))
        else:
            raise ValueError("flat(): Flat does not support values of type %s" % type(arg))
    return ''.join(out)

def isprint(c):
    """isprint(c) -> bool

    Return True if a character is printable"""
    return c in string.ascii_letters + string.digits + string.punctuation + ' '

def _hexiichar(c):
    HEXII = string.punctuation + string.digits + string.ascii_lowercase + string.ascii_uppercase
    if c in HEXII:
        return ".%c " % c
    elif c == '\0':
        return "   "
    elif c == '\xff':
        return "## "
    else:
        return "%02x " % ord(c)

def hexdump_iter(logger, fd, width=16, skip=True, hexii=False, begin=0, highlight=None):
    r"""
    Return a hexdump-dump of a string as a generator of lines.  Unless you have
    massive amounts of data you probably want to use :meth:`hexdump`.

    Arguments:
        logger(FastLogger): Logger object
        fd(file): File object to dump.  Use :meth:`StringIO.StringIO` or :meth:`hexdump` to dump a string.
        width(int): The number of characters per line
        skip(bool): Set to True, if repeated lines should be replaced by a "*"
        hexii(bool): Set to True, if a hexii-dump should be returned instead of a hexdump.
        begin(int):  Offset of the first byte to print in the left column
        highlight(iterable): Byte values to highlight.

    Returns:
        A generator producing the hexdump-dump one line at a time.
    """
    style     = logger.style.hexdump.copy()
    highlight = highlight or []

    for b in highlight:
        if isinstance(b, str):
            b = ord(b)
        style['%02x' % b] = style['highlight']

    _style = style

    skipping    = False
    lines       = []
    last_unique = ''
    byte_width  = len('00 ')
    column_sep  = '  '
    line_fmt    = '%%(offset)08x  %%(hexbytes)-%is │%%(printable)s│' % (len(column_sep)+(width*byte_width))
    spacer      = ' '
    marker      = (style.get('marker') or (lambda s:s))('│')

    if hexii:
        column_sep = ''
        line_fmt   = '%%(offset)08x  %%(hexbytes)-%is│' % (len(column_sep)+(width*byte_width))
    else:
        def style_byte(b):
            hbyte = '%02x' % ord(b)
            abyte = b if isprint(b) else '·'
            if hbyte in style:
                st = style[hbyte]
            elif isprint(b):
                st = style.get('printable')
            else:
                st = style.get('nonprintable')
            if st:
                hbyte = st(hbyte)
                abyte = st(abyte)
            return hbyte, abyte
        cache = [style_byte(chr(b)) for b in range(256)]

    numb = 0
    while True:
        offset = begin + numb

        # If a tube is passed in as fd, it will raise EOFError when it runs
        # out of data, unlike a file or StringIO object, which return an empty
        # string.
        try:
            chunk = fd.read(width)
        except EOFError:
            chunk = ''

        # We have run out of data, exit the loop
        if chunk == '':
            break

        # Advance the cursor by the number of bytes we actually read
        numb += len(chunk)

        # If this chunk is the same as the last unique chunk,
        # use a '*' instead.
        if skip and last_unique:
            same_as_last_line = (last_unique == chunk)
            lines_are_sequential = False
            last_unique = chunk

            if same_as_last_line or lines_are_sequential:

                # If we have not already printed a "*", do so
                if not skipping:
                    yield '*'
                    skipping = True

                # Move on to the next chunk
                continue

        # Chunk is unique, no longer skipping
        skipping = False
        last_unique = chunk

        # Generate contents for line
        hexbytes = ''
        printable = ''
        for i, b in enumerate(chunk):
            if not hexii:
                hbyte, abyte = cache[ord(b)]
            else:
                hbyte, abyte = _hexiichar(b), ''

            if i % 4 == 3 and i < width - 1:
                hbyte += spacer
                abyte += marker

            hexbytes += hbyte + ' '
            printable += abyte

        if i + 1 < width:
            delta = width - i - 1

            # How many hex-bytes would we have printed?
            count = byte_width * delta

            # How many dividers do we need to fill out the line?
            dividers_per_line = (width // 4) - (1 if width % 4 == 0 else 0)
            dividers_printed = (i // 4) + (1 if i % 4 == 3 else 0)
            count += dividers_per_line - dividers_printed

            hexbytes += ' ' * count

        # Python2 -> 3 wew
        if isinstance(line_fmt, six.binary_type):
            line_fmt = line_fmt.decode('utf-8')
        if isinstance(offset, six.binary_type):
            offset = printable.decode('utf-8')
        
        line = line_fmt % {'offset': offset, 'hexbytes': hexbytes, 'printable': printable}
        yield line

    line = "%08x" % (begin + numb)
    yield line

def hexdump(logger, s, width=16, skip=True, hexii=False, begin=0, highlight=None):
    r"""
    Return a hexdump-dump of a string.

    Arguments:
        logger(FastLogger): Logger object
        s(str): The data to hexdump.
        width(int): The number of characters per line
        skip(bool): Set to True, if repeated lines should be replaced by a "*"
        hexii(bool): Set to True, if a hexii-dump should be returned instead of a hexdump.
        begin(int):  Offset of the first byte to print in the left column
        highlight(iterable): Byte values to highlight.

    Returns:
        A hexdump-dump in the form of a string.

    Examples:

        >>> print hexdump("abc")
        00000000  61 62 63                                            │abc│
        00000003

        >>> print hexdump('A'*32)
        00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA│AAAA│AAAA│AAAA│
        *
        00000020

        >>> print hexdump('A'*32, width=8)
        00000000  41 41 41 41  41 41 41 41   │AAAA│AAAA│
        *
        00000020

        >>> print hexdump(list(map(chr, range(256))))
        00000000  00 01 02 03  04 05 06 07  08 09 0a 0b  0c 0d 0e 0f  │····│····│····│····│
        00000010  10 11 12 13  14 15 16 17  18 19 1a 1b  1c 1d 1e 1f  │····│····│····│····│
        00000020  20 21 22 23  24 25 26 27  28 29 2a 2b  2c 2d 2e 2f  │ !"#│$%&'│()*+│,-./│
        00000030  30 31 32 33  34 35 36 37  38 39 3a 3b  3c 3d 3e 3f  │0123│4567│89:;│<=>?│
        00000040  40 41 42 43  44 45 46 47  48 49 4a 4b  4c 4d 4e 4f  │@ABC│DEFG│HIJK│LMNO│
        00000050  50 51 52 53  54 55 56 57  58 59 5a 5b  5c 5d 5e 5f  │PQRS│TUVW│XYZ[│\]^_│
        00000060  60 61 62 63  64 65 66 67  68 69 6a 6b  6c 6d 6e 6f  │`abc│defg│hijk│lmno│
        00000070  70 71 72 73  74 75 76 77  78 79 7a 7b  7c 7d 7e 7f  │pqrs│tuvw│xyz{│|}~·│
        00000080  80 81 82 83  84 85 86 87  88 89 8a 8b  8c 8d 8e 8f  │····│····│····│····│
        00000090  90 91 92 93  94 95 96 97  98 99 9a 9b  9c 9d 9e 9f  │····│····│····│····│
        000000a0  a0 a1 a2 a3  a4 a5 a6 a7  a8 a9 aa ab  ac ad ae af  │····│····│····│····│
        000000b0  b0 b1 b2 b3  b4 b5 b6 b7  b8 b9 ba bb  bc bd be bf  │····│····│····│····│
        000000c0  c0 c1 c2 c3  c4 c5 c6 c7  c8 c9 ca cb  cc cd ce cf  │····│····│····│····│
        000000d0  d0 d1 d2 d3  d4 d5 d6 d7  d8 d9 da db  dc dd de df  │····│····│····│····│
        000000e0  e0 e1 e2 e3  e4 e5 e6 e7  e8 e9 ea eb  ec ed ee ef  │····│····│····│····│
        000000f0  f0 f1 f2 f3  f4 f5 f6 f7  f8 f9 fa fb  fc fd fe ff  │····│····│····│····│
        00000100

        >>> print hexdump(list(map(chr, range(256))), hexii=True)
        00000000      01  02  03   04  05  06  07   08  09  0a  0b   0c  0d  0e  0f  │
        00000010  10  11  12  13   14  15  16  17   18  19  1a  1b   1c  1d  1e  1f  │
        00000020  20  .!  ."  .#   .$  .%  .&  .'   .(  .)  .*  .+   .,  .-  ..  ./  │
        00000030  .0  .1  .2  .3   .4  .5  .6  .7   .8  .9  .:  .;   .<  .=  .>  .?  │
        00000040  .@  .A  .B  .C   .D  .E  .F  .G   .H  .I  .J  .K   .L  .M  .N  .O  │
        00000050  .P  .Q  .R  .S   .T  .U  .V  .W   .X  .Y  .Z  .[   .\  .]  .^  ._  │
        00000060  .`  .a  .b  .c   .d  .e  .f  .g   .h  .i  .j  .k   .l  .m  .n  .o  │
        00000070  .p  .q  .r  .s   .t  .u  .v  .w   .x  .y  .z  .{   .|  .}  .~  7f  │
        00000080  80  81  82  83   84  85  86  87   88  89  8a  8b   8c  8d  8e  8f  │
        00000090  90  91  92  93   94  95  96  97   98  99  9a  9b   9c  9d  9e  9f  │
        000000a0  a0  a1  a2  a3   a4  a5  a6  a7   a8  a9  aa  ab   ac  ad  ae  af  │
        000000b0  b0  b1  b2  b3   b4  b5  b6  b7   b8  b9  ba  bb   bc  bd  be  bf  │
        000000c0  c0  c1  c2  c3   c4  c5  c6  c7   c8  c9  ca  cb   cc  cd  ce  cf  │
        000000d0  d0  d1  d2  d3   d4  d5  d6  d7   d8  d9  da  db   dc  dd  de  df  │
        000000e0  e0  e1  e2  e3   e4  e5  e6  e7   e8  e9  ea  eb   ec  ed  ee  ef  │
        000000f0  f0  f1  f2  f3   f4  f5  f6  f7   f8  f9  fa  fb   fc  fd  fe  ##  │
        00000100

        >>> print hexdump('X' * 64)
        00000000  58 58 58 58  58 58 58 58  58 58 58 58  58 58 58 58  │XXXX│XXXX│XXXX│XXXX│
        *
        00000040

        >>> print hexdump('X' * 64, skip=False)
        00000000  58 58 58 58  58 58 58 58  58 58 58 58  58 58 58 58  │XXXX│XXXX│XXXX│XXXX│
        00000010  58 58 58 58  58 58 58 58  58 58 58 58  58 58 58 58  │XXXX│XXXX│XXXX│XXXX│
        00000020  58 58 58 58  58 58 58 58  58 58 58 58  58 58 58 58  │XXXX│XXXX│XXXX│XXXX│
        00000030  58 58 58 58  58 58 58 58  58 58 58 58  58 58 58 58  │XXXX│XXXX│XXXX│XXXX│
        00000040

        >>> print hexdump(fit({0x10: 'X'*0x20, 0x50-1: '\xff'*20}, length=0xc0) + '\x00'*32, cyclic=1, hexii=1)
        00000000  .a  .a  .a  .a   .b  .a  .a  .a   .c  .a  .a  .a   .d  .a  .a  .a  │
        00000010  .X  .X  .X  .X   .X  .X  .X  .X   .X  .X  .X  .X   .X  .X  .X  .X  │
        *
        00000030  .m  .a  .a  .a   .n  .a  .a  .a   .o  .a  .a  .a   .p  .a  .a  .a  │
        00000040  .q  .a  .a  .a   .r  .a  .a  .a   .s  .a  .a  .a   .t  .a  .a  ##  │
        00000050  ##  ##  ##  ##   ##  ##  ##  ##   ##  ##  ##  ##   ##  ##  ##  ##  │
        00000060  ##  ##  ##  .a   .z  .a  .a  .b   .b  .a  .a  .b   .c  .a  .a  .b  │
        00000070  .d  .a  .a  .b   .e  .a  .a  .b   .f  .a  .a  .b   .g  .a  .a  .b  │
        *
        000000c0                                                                     │
        *
        000000e0

        >>> print hexdump('A'*16, width=9)
        00000000  41 41 41 41  41 41 41 41  41  │AAAA│AAAA│A│
        00000009  41 41 41 41  41 41 41         │AAAA│AAA│
        00000010
        >>> print hexdump('A'*16, width=10)
        00000000  41 41 41 41  41 41 41 41  41 41  │AAAA│AAAA│AA│
        0000000a  41 41 41 41  41 41               │AAAA│AA│
        00000010
        >>> print hexdump('A'*16, width=11)
        00000000  41 41 41 41  41 41 41 41  41 41 41  │AAAA│AAAA│AAA│
        0000000b  41 41 41 41  41                     │AAAA│A│
        00000010
        >>> print hexdump('A'*16, width=12)
        00000000  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA│AAAA│AAAA│
        0000000c  41 41 41 41                            │AAAA││
        00000010
        >>> print hexdump('A'*16, width=13)
        00000000  41 41 41 41  41 41 41 41  41 41 41 41  41  │AAAA│AAAA│AAAA│A│
        0000000d  41 41 41                                   │AAA│
        00000010
        >>> print hexdump('A'*16, width=14)
        00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41  │AAAA│AAAA│AAAA│AA│
        0000000e  41 41                                         │AA│
        00000010
        >>> print hexdump('A'*16, width=15)
        00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41  │AAAA│AAAA│AAAA│AAA│
        0000000f  41                                               │A│
        00000010
    """
    s = _flat(s)
    return '\n'.join(hexdump_iter(logger, StringIO(s),
                                  width,
                                  skip,
                                  hexii,
                                  begin,
                                  highlight))
