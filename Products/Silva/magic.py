# Copyright (c) 2009-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os.path
import mimetypes

mimetypes.init()

class IdGuess(object):

    def __init__(self, *kw):
        pass

    def guess(self, id=None, filename=None, buffer=None, default=None):
        if id:
            type, enc = mimetypes.guess_type(id)
            if type is not None:
                return type, enc
        if filename is not None:
            type = self.file(filename)
        elif buffer is not None:
            type = self.buffer(buffer)
        if type is not None:
            return type, None
        if default is not None:
            return default, None
        return 'application/octet-stream', None

    def buffer(self, buffer):
        return None

    def file(self, filename):
        return None

try:

    import ctypes
    import ctypes.util
    from ctypes import c_char_p, c_int, c_size_t, c_void_p

    class MagicException(Exception):
        pass

    libmagic_path = ctypes.util.find_library('magic')
    if libmagic_path is None:
        raise ImportError(u"libmagic not available")
    libmagic = ctypes.CDLL(libmagic_path)

    magic_t = ctypes.c_void_p

    magic_error = libmagic.magic_error
    magic_error.restype = c_char_p
    magic_error.argtypes = [magic_t]

    def error_check(result, func, args):
        err = magic_error(args[0])
        if err is not None:
            raise MagicException(err)
        else:
            return result

    magic_open = libmagic.magic_open
    magic_open.restype = magic_t
    magic_open.argtypes = [c_int]

    magic_close = libmagic.magic_close
    magic_close.restype = None
    magic_close.argtypes = [magic_t]
    magic_close.errcheck = error_check

    magic_file = libmagic.magic_file
    magic_file.restype = c_char_p
    magic_file.argtypes = [magic_t, c_char_p]
    magic_file.errcheck = error_check

    magic_buffer = libmagic.magic_buffer
    magic_buffer.restype = c_char_p
    magic_buffer.argtypes = [magic_t, c_void_p, c_size_t]
    magic_buffer.errcheck = error_check

    magic_load = libmagic.magic_load
    magic_load.restype = c_int
    magic_load.argtypes = [magic_t, c_char_p]
    magic_load.errcheck = error_check

    MAGIC_MIME = 0x000010 # Return a mime string
    HAVE_MAGIC = True

    class MagicGuess(IdGuess):

        def __init__(self, magic_file=None):
            flags = MAGIC_MIME
            self.cookie = magic_open(flags)
            magic_load(self.cookie, magic_file)

        def buffer(self, buf):
            return magic_buffer(self.cookie, buf, len(buf))

        def file(self, filename):
            if not os.path.exists(filename):
                raise IOError("File does not exist: " + filename)

            return magic_file(self.cookie, filename)

except (OSError, ImportError, AttributeError):

    HAVE_MAGIC = False

    class MagicGuess(IdGuess):

        def buffer(self, buf):
            if str(buf)[:5] == '%PDF-':
                return 'application/pdf'
            elif buf.startswith('<?xml'):
                return 'text/xml'
            return 'application/octet-stream'

        def file(self, filename):
            fd = open(filename)
            return self.buffer(fd.read(5))

