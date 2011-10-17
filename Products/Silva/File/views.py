# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.datetime import time as time_from_datetime
from zope.publisher.interfaces.browser import IBrowserRequest

from webdav.common import rfc1123_date
from ZPublisher.Iterators import IStreamIterator

from Products.Silva.File.content import CHUNK_SIZE
from Products.Silva.File.content import File, BlobFile, ZODBFile
from silva.core import interfaces
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders


class FDIterator(object):
    """This object provides an iterator on file descriptors.
    """
    grok.implements(IStreamIterator)

    def __init__(self, fd, close=True):
        self.__fd = fd
        self.__close = close
        self.__closed = False

    def __iter__(self):
        return self

    def next(self):
        if self.__closed:
            raise StopIteration
        data = self.__fd.read(CHUNK_SIZE)
        if not data:
            if self.__close:
                self.__fd.close()
                self.__closed = True
            raise StopIteration
        return data


class FileResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IBrowserRequest, interfaces.IFile)

    def other_headers(self, headers):
        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (self.context.get_filename()))
        self.response.setHeader(
            'Content-Type', self.context.get_content_type())
        if self.context.get_content_encoding():
            self.response.setHeader(
                'Content-Encoding', self.context.get_content_encoding())
        self.response.setHeader(
            'Content-Length', self.context.get_file_size())
        self.response.setHeader(
            'Last-Modified',
            rfc1123_date(self.context.get_modification_datetime()))
        self.response.setHeader(
            'Accept-Ranges', None)


class DefaultFileView(silvaviews.View):
    """View a File in the SMI / preview. For this just return a tag.

    Note that if you directly access the URL of the file, you will
    download its content (See the independent index view below for
    each storage).
    """
    grok.context(File)
    grok.require('zope2.View')

    def render(self):
        return self.content.tag()



class ZODBFileView(silvaviews.View):
    """Download a ZODBFile
    """
    grok.context(ZODBFile)
    grok.require('zope2.View')
    grok.name('index.html')

    def render(self):
        # XXX This should not be required
        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (self.context.get_filename()))
        return self.context._file.index_html(self.request, self.response)


class BlobFileView(silvaviews.View):
    """Download a BlobFile.
    """
    grok.context(BlobFile)
    grok.require('zope2.View')
    grok.name('index.html')

    def render(self):
        header = self.request.environ.get('HTTP_IF_MODIFIED_SINCE', None)
        if header is not None:
            header = header.split(';')[0]
            try:
                mod_since = long(time_from_datetime(header))
            except:
                mod_since = None
            if mod_since is not None:
                last_mod = self.context.get_modification_datetime()
                if last_mod is not None:
                    last_mod = long(last_mod)
                    if last_mod > 0 and last_mod <= mod_since:
                        self.response.setStatus(304)
                        return u''
        return FDIterator(self.context.get_file_fd())

