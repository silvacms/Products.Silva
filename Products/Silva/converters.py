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


def get_converter_for_mimetype(mimetype):
    """Return the given converter for a given mimetype.
    """
    converter = {
        'text/plain': TextConverter,
        'application/pdf':PDFConverter,
        'application/msword':WordConverter
    }.get(mimetype)

    if converter is None:
        return
    return converter()


class WordConverter(object):
    """Convert a word document to fulltext using antiword.
    """

    def convert(self, data, request):
        if not WORD_TO_TEXT_AVAILABLE:
            return
        fname = tempfile.mktemp('.doc', 'silva_')
        fp = open(fname, 'w+b')
        fp.write(data)
        fp.close()
        converted, err = execute('antiword "%s"' % fname)
        os.unlink(fname)
        if err:
            request.form['message_type'] = 'feedback'
            request.form['message'] = "The file was uploaded successfully " \
                "but could not be indexed properly for the search."
        try:
            if converted:
                decoded = unicode(converted, 'utf8')
                return decoded
            return None
        except UnicodeDecodeError:
            return None


class PDFConverter(object):
    """Converter for pdf files, which extract the text of a PDF file
    using pdftotext.
    """

    def convert(self, data, request):
        if not PDF_TO_TEXT_AVAILABLE:
            return
        fname = tempfile.mktemp('.pdf', 'silva_')
        fp = open(fname, 'w+b')
        fp.write(data)
        fp.close()
        converted, err = execute('pdftotext -enc UTF-8 "%s" -' % fname)
        os.unlink(fname)
        if err:
            request.form['message_type'] = 'feedback'
            request.form['message'] = "The file was uploaded successfully " \
                "but could not be indexed properly for the search."
        try:
            if converted:
                decoded = unicode(converted, 'utf8')
                return decoded
            return None
        except UnicodeDecodeError:
            return None


class TextConverter(object):
    """Fallback convert for text file, which does nothing.
    """

    def convert(self, data, request):
        try:
            decoded = unicode(data, 'utf8')
            return decoded
        except UnicodeDecodeError:
            return None

