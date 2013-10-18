# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from __future__ import absolute_import

import logging
import os.path
import mimetypes

from App.config import getConfiguration
from silva.core.interfaces import IMimeTypeClassifier
from zope.interface import implements


logger = logging.getLogger('silva.core')

_DEFAULT_MIME_TYPES = [
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

_ENCODING_MIMETYPE_TO_ENCODING = {
    'application/x-gzip': 'gzip',
    'application/x-bzip2': 'bzip2',
    }
_CONTENT_ENCODING_EXT = {
    'gzip': '.gz',
    'bzip2': '.bz'
    }
_EXT_CONTENT_ENCODING = {
    '.gz': 'gzip',
    '.bz': 'bzip2'
    }


class NonDefaultMimeTypes(mimetypes.MimeTypes):

    def __init__(self, filename):
        self.encodings_map = mimetypes.encodings_map.copy()
        self.suffix_map = mimetypes.suffix_map.copy()
        self.types_map = ({}, {})  # dict for (non-strict, strict)
        self.types_map_inv = ({}, {})
        self.read(filename, True)


class BaseMimeTypeClassifier(object):
    implements(IMimeTypeClassifier)

    def __init__(self, **options):
        self.types = NonDefaultMimeTypes(
            options.get('mime_types', '/etc/mime.types'))

    def guess_filename(self, asset, basename):
        # This function is here to be usable by File and Image
        if not asset.get_file_size():
            return None

        extension = None
        guessed_extension = None
        original_name = asset.get_filename()
        content_type = asset.get_content_type()
        content_encoding = asset.get_content_encoding()

        if '.' in basename:
            basename, extension = os.path.splitext(basename)
            if extension in _EXT_CONTENT_ENCODING and '.' in basename:
                if content_encoding is None:
                    content_encoding = _EXT_CONTENT_ENCODING[extension]
                basename, extension = os.path.splitext(basename)
        elif '.' in original_name:
            tmp_name, extension = os.path.splitext(original_name)
            if extension in _EXT_CONTENT_ENCODING and '.' in tmp_name:
                if content_encoding is None:
                    content_encoding = _EXT_CONTENT_ENCODING[extension]
                tmp_name, extension = os.path.splitext(tmp_name)
        if extension:
            extension = extension.lower()

        # application/octet-stream is the default, we ignore it.
        if content_type != 'application/octet-stream':
            guessed_extension = self.guess_extension(content_type)
        # Compression extension are not reconized by mimetypes use an
        # extra table for them.
        if guessed_extension is None:
            if (content_type in _ENCODING_MIMETYPE_TO_ENCODING and
                    content_encoding is None):
                # Compression extension often are used with some other
                # extension. Unfortunately, at this point we might have
                # lost that other extension. The editor has to rename
                # properly the file.
                content_encoding = _ENCODING_MIMETYPE_TO_ENCODING[content_type]
        elif guessed_extension is not None:
            # If we didn't have an extension, or the extension is not
            # a compatible one with the previous one, update it.
            if (extension is None or
                (extension != guessed_extension and
                 extension not in self.guess_all_extensions(content_type))):
                extension = guessed_extension
        if extension is not None:
            basename += extension
        if (content_encoding is not None and
                content_encoding in _CONTENT_ENCODING_EXT):
            basename += _CONTENT_ENCODING_EXT[content_encoding]
        if basename != original_name:
            asset.set_filename(basename)
        return basename

    def guess_extension(self, content_type):
        return self.types.guess_extension(content_type)

    def guess_all_extensions(self, content_type):
        return self.types.guess_all_extensions(content_type)

    def guess_type(self, id=None, filename=None, buffer=None, default=None):
        if id:
            mimetype, encoding = self.types.guess_type(id)
            if mimetype is not None:
                return mimetype, encoding
        if filename is not None:
            mimetype, encoding = self.guess_file_type(filename)
        elif buffer is not None:
            mimetype, encoding = self.guess_buffer_type(buffer)
        if mimetype is not None:
            return mimetype, encoding
        if default is not None:
            return default, None
        return 'application/octet-stream', None

    def guess_buffer_type(self, buffer):
        return None, None

    def guess_file_type(self, filename):
        return None, None

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
        if result is None:
            error = magic_error(args[0])
            raise MagicException(error)
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

    MAGIC_MIME = 0x000010  # Return a mime string
    MAGIC_COMPRESS = 0x000004
    HAVE_MAGIC = True

    class MimeTypeClassifier(BaseMimeTypeClassifier):

        def __init__(self, **options):
            super(MimeTypeClassifier, self).__init__(**options)
            magic_file = options.get('magic_file')
            magic_flags = MAGIC_MIME
            self.options = magic_open(magic_flags)
            self.compressed_options = magic_open(magic_flags | MAGIC_COMPRESS)
            magic_load(self.options, magic_file)
            magic_load(self.compressed_options, magic_file)

        def guess_buffer_type(self, buffer):
            try:
                mimetype = magic_buffer(self.options, buffer, len(buffer))
                encoding = None
                if mimetype in _ENCODING_MIMETYPE_TO_ENCODING:
                    encoding = _ENCODING_MIMETYPE_TO_ENCODING[mimetype]
                    mimetype = magic_buffer(
                        self.compressed_options, buffer, len(buffer))
                return mimetype, encoding
            except MagicException as error:
                logger.error(
                    u"Error while detecting mimetype for a buffer: %s",
                    str(error))
                return None, None

        def guess_file_type(self, filename):
            if not os.path.exists(filename):
                raise IOError("File does not exist: " + filename)

            try:
                mimetype = magic_file(self.options, filename)
                encoding = None
                if mimetype in _ENCODING_MIMETYPE_TO_ENCODING:
                    encoding = _ENCODING_MIMETYPE_TO_ENCODING[mimetype]
                    mimetype = magic_file(self.compressed_options, filename)
                return mimetype, encoding
            except MagicException as error:
                logger.error(
                    u"Error while detecting mimetype for a file: %s, %s",
                    str(error), filename)
                return None, None

except (OSError, ImportError, AttributeError):

    HAVE_MAGIC = False

    class MimeTypeClassifier(BaseMimeTypeClassifier):

        def guess_buffer_type(self, buf):
            if str(buf)[:5] == '%PDF-':
                return 'application/pdf', None
            elif buf.startswith('<?xml'):
                return 'text/xml', None
            return 'application/octet-stream', None

        def guess_file_type(self, filename):
            fd = open(filename)
            return self.buffer(fd.read(5))


def MimeTypeClassifierFactory():
    zconf = getattr(getConfiguration(), 'product_config', {})
    config = zconf.get('silva', {})
    mime_types = config.get('mime_types')
    magic_file = config.get('magic_file')
    if mime_types is None:
        for candidate in _DEFAULT_MIME_TYPES:
            if os.path.isfile(candidate):
                mime_types = candidate
                break
        else:
            raise RuntimeError(
                u"Cannot find a mime.types file. "
                u"Please add a configuration entry pointing to one.")
    logger.warn('Using mime.types from %s', mime_types)
    return MimeTypeClassifier(mime_types=mime_types, magic_file=magic_file)
