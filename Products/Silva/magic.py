# Copyright (c) 2009-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging
import os.path
import mimetypes

from App.config import getConfiguration
from silva.core.interfaces import IMimeTypeClassifier
from zope.interface import implements


logger = logging.getLogger('silva.core')

default_mime_types = [
    '/etc/mime.types',
    "/usr/local/etc/mime.types",
    "/etc/httpd/mime.types",
    "/etc/httpd/conf/mime.types",
    "/etc/apache/mime.types",
    "/etc/apache2/mime.types",
    "/usr/local/etc/httpd/conf/mime.types",
    "/usr/local/lib/netscape/mime.types",
    "/usr/local/etc/httpd/conf/mime.types",
    ]


class NonDefaultMimeTypes(mimetypes.MimeTypes):

    def __init__(self, filename):
        self.encodings_map = mimetypes.encodings_map.copy()
        self.suffix_map = mimetypes.suffix_map.copy()
        self.types_map = ({}, {}) # dict for (non-strict, strict)
        self.types_map_inv = ({}, {})
        self.read(filename, True)


class BaseMimeTypeClassifier(object):
    implements(IMimeTypeClassifier)

    def __init__(self, mimes_file='/etc/mime.types'):
        self.types = NonDefaultMimeTypes(mimes_file)

    def guess_extension(self, content_type):
        return self.types.guess_extension(content_type)

    def guess_type(self, id=None, filename=None, buffer=None, default=None):
        if id:
            type, enc = self.types.guess_type(id)
            if type is not None:
                return type, enc
        if filename is not None:
            type = self.guess_file_type(filename)
        elif buffer is not None:
            type = self.guess_buffer_type(buffer)
        if type is not None:
            return type, None
        if default is not None:
            return default, None
        return 'application/octet-stream', None

    def guess_buffer_type(self, buffer):
        return None

    def guess_file_type(self, filename):
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

    class MimeTypeClassifier(BaseMimeTypeClassifier):

        def __init__(self, mimes_file='/etc/mime.types', magic_file=None):
            super(MimeTypeClassifier, self).__init__(mimes_file)
            flags = MAGIC_MIME
            self.cookie = magic_open(flags)
            magic_load(self.cookie, magic_file)

        def guess_buffer_type(self, buf):
            return magic_buffer(self.cookie, buf, len(buf))

        def guess_file_type(self, filename):
            if not os.path.exists(filename):
                raise IOError("File does not exist: " + filename)

            return magic_file(self.cookie, filename)

except (OSError, ImportError, AttributeError):

    HAVE_MAGIC = False

    class MimeTypeClassifier(BaseMimeTypeClassifier):

        def guess_buffer_type(self, buf):
            if str(buf)[:5] == '%PDF-':
                return 'application/pdf'
            elif buf.startswith('<?xml'):
                return 'text/xml'
            return 'application/octet-stream'

        def guess_file_type(self, filename):
            fd = open(filename)
            return self.buffer(fd.read(5))

def MimeTypeClassifierFactory():
    zconf = getattr(getConfiguration(), 'product_config', {})
    config = zconf.get('silva', {})
    mime_types = config.get('mime_types')
    if mime_types is None:
        for candidate in default_mime_types:
            if os.path.isfile(candidate):
                mime_types = candidate
                break
        else:
            raise RuntimeError(
                u"Cannot find a mime.types file. "
                u"Please add a configuration entry pointing to one.")
    logger.info('Using mime.types from %s', mime_types)
    return MimeTypeClassifier(mime_types)
