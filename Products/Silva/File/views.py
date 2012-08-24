# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.datetime import time as time_from_datetime
from zope.publisher.interfaces.browser import IBrowserRequest

from webdav.common import rfc1123_date
from ZPublisher.Iterators import IStreamIterator
from ZPublisher.HTTPRangeSupport import parseRange, expandRanges

from Products.Silva.File.content import CHUNK_SIZE
from Products.Silva.File.content import File, BlobFile, ZODBFile
from silva.core import interfaces
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders


class BlobIterator(object):
    """This object provides an iterator on file descriptors.
    """
    grok.implements(IStreamIterator)

    def __init__(self, fd, close=True, start=None, end=None):
        self.__fd = fd
        self.__close = close
        self.__closed = False
        self.__position = 0
        self.__end = end
        if start is not None:
            self.__position = start
            self.__fd.seek(start, 0)

    def __iter__(self):
        return self

    def next(self):
        if self.__closed:
            raise StopIteration
        size = CHUNK_SIZE
        data = None
        if self.__end is not None:
            size = max(min(CHUNK_SIZE, self.__end - self.__position), 0)
            self.__position += size
        if size:
            data = self.__fd.read(size)
        if not data:
            if self.__close:
                self.__fd.close()
                self.__closed = True
            raise StopIteration
        return data


class OFSPayloadIterator(object):
    grok.implements(IStreamIterator)

    def __init__(self, payload):
        self.__payload = payload

    def __iter__(self):
        return self

    def next(self):
        if self.__payload is not None:
            data = self.__payload.data
            self.__payload = self.__payload.next
            return data
        raise StopIteration


class FileResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IBrowserRequest, interfaces.IFile)

    def other_headers(self, headers):
        self.response.setHeader(
            'Last-Modified',
            rfc1123_date(self.context.get_modification_datetime()))
        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (self.context.get_filename()))
        self.response.setHeader(
            'Content-Type',
            self.context.get_content_type())
        if self.context.get_content_encoding():
            self.response.setHeader(
                'Content-Encoding',
                self.context.get_content_encoding())
        if not self.response.getHeader('Content-Length'):
            self.response.setHeader(
                'Content-Length',
                self.context.get_file_size())
        if not self.response.getHeader('Accept-Ranges'):
            self.response.setHeader(
                'Accept-Ranges',
                'none')


class FileView(silvaviews.View):
    """View a File in the SMI / preview. For this just return a tag.

    Note that if you directly access the URL of the file, you will
    download its content (See the independent index view below for
    each storage).
    """
    grok.context(File)
    grok.require('zope2.View')

    def render(self):
        return self.content.tag()


class FileDownloadView(silvaviews.View):
    grok.baseclass()
    grok.require('zope2.View')
    grok.name('index.html')

    def is_not_modified(self):
        """Return true if the file was not modified since the date
        given in the request headers.
        """
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
                        return True
        return False

    def have_ranges(self):
        header = self.request.environ.get('HTTP_RANGE', None)
        if header is not None:
            ranges = parseRange(header)
            if len(ranges) == 1:
                size = self.context.get_file_size()
                satisfiable = expandRanges(ranges, size)
                if len(satisfiable) == 1:
                    return (satisfiable[0][0], satisfiable[0][1] - 1, size)
                return (None, None, size)
        return (None, None, None)

    def payload(self):
        raise NotImplementedError

    def render(self):
        if self.is_not_modified():
            self.response.setStatus(304)
            return u''
        return self.payload()


class ZODBFileDownloadView(FileDownloadView):
    """Download a ZODBFile
    """
    grok.context(ZODBFile)

    def payload(self):
        payload = self.context._file.data
        if isinstance(payload, str):
            return payload
        return OFSPayloadIterator(payload)


class BlobFileDownloadView(FileDownloadView):
    """Download a BlobFile.
    """
    grok.context(BlobFile)

    def payload(self):
        self.response.setHeader(
            'Accept-Ranges',
            'bytes')
        start, end, size = self.have_ranges()
        if size is not None:
            if start is None:
                self.response.setStatus(416)
                self.response.setHeader(
                    'Content-Range',
                    'bytes */%d' % size)
                return u''
            self.response.setStatus(206)
            self.response.setHeader(
                'Content-Length',
                str(end - start))
            self.response.setHeader(
                'Content-Range',
                'bytes %d-%d/%d' % (start, end, size))
        return BlobIterator(self.context.get_file_fd(), start=start, end=end)

    def render(self):
        if self.is_not_modified():
            self.response.setStatus(304)
            return u''
        return self.payload()
