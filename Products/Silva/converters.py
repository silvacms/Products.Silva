# -*- coding: utf-8 -*-
# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os, tempfile, subprocess


def execute(cmd):
    """Execute the given command in a shell, and give back a tuple
    (stdout, stderr).
    """
    process =  subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()


def have_command(cmd):
    """Test if the given command is available.
    """
    return execute('%s -v' % cmd)[1].strip() != '%s: not found' % cmd


PDF_TO_TEXT_AVAILABLE = have_command('pdftotext')
WORD_TO_TEXT_AVAILABLE = have_command('antiword')


def get_converter_for_mimetype(mimetype, request):
    """Return the given converter for a given mimetype.
    """
    factory = {
        'text/plain': TextConverter,
        'application/pdf': PDFConverter,
        'application/msword': WordConverter
    }.get(mimetype)

    if factory is None:
        return None
    converter = factory(request)
    if not converter.available():
        return None
    return converter


class Converter(object):

    def __init__(self, request):
        self.request = request

    def available(self):
        return True

    def convert_file(self, filename):
        raise NotImplementedError

    def convert_string(self, data):
        raise NotImplementedError


class WordConverter(Converter):
    """Convert a word document to fulltext using antiword.
    """

    def available(self):
        return WORD_TO_TEXT_AVAILABLE

    def convert_file(self, filename):
        converted, errors = execute('antiword "%s"' % filename)
        if errors:
            self.request.form['message_type'] = 'feedback'
            self.request.form['message'] = "The file was uploaded successfully " \
                "but could not be indexed properly for the search."
        if converted:
            try:
                return unicode(converted, 'utf8')
            except UnicodeDecodeError:
                pass
        return None

    def convert_string(self, data):
        filename = tempfile.mktemp('.doc', 'silva_')
        fp = open(filename, 'w+b')
        fp.write(data)
        fp.close()
        try:
            return self.convert_file(filename)
        finally:
            os.unlink(filename)


class PDFConverter(Converter):
    """Converter for pdf files, which extract the text of a PDF file
    using pdftotext.
    """

    def available(self):
        return PDF_TO_TEXT_AVAILABLE

    def convert_file(self, filename):
        converted, errors = execute('pdftotext -enc UTF-8 "%s" -' % filename)
        if errors:
            self.request.form['message_type'] = 'feedback'
            self.request.form['message'] = "The file was uploaded successfully " \
                "but could not be indexed properly for the search."
        if converted:
            try:
                return unicode(converted, 'utf8')
            except UnicodeDecodeError:
                pass
        return None

    def convert_string(self, data):
        filename = tempfile.mktemp('.pdf', 'silva_')
        fp = open(filename, 'w+b')
        fp.write(data)
        fp.close()
        try:
            return self.convert_file(filename)
        finally:
            os.unlink(filename)


class TextConverter(Converter):
    """Fallback convert for text file, which does nothing.
    """

    def convert_file(self, filename):
        fp = None
        try:
            fp = open(filename, 'r')
            return unicode(fp.read(), 'utf-8')
        except (OSError, UnicodeDecodeError):
            return None
        finally:
            fp.clone()

    def convert_data(self, data):
        try:
            return unicode(data, 'utf8')
        except UnicodeDecodeError:
            return None

