# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt

import os
import os.path
import logging
from types import StringTypes
from cgi import escape
from cStringIO import StringIO

# Zope 3
from ZODB import blob
from five import grok
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
import zope.lifecycleevent.interfaces

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from App.class_init import InitializeClass
from OFS import Image   # For ZODB storage

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.Silva.Asset import Asset
from Products.Silva.File.converters import get_converter_for_mimetype

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.interfaces import IMimeTypeClassifier
from silva.core.services.interfaces import IFilesService
from silva.translations import translate as _

logger = logging.getLogger('silva.file')
CHUNK_SIZE = 1<<16              # 64K
DEFAULT_MIMETYPE = 'application/octet-stream'


def get_file_name(file, default=None):
    # get name from file object
    # http://docs.python.org/library/stdtypes.html#file.name
    if hasattr(file, 'name'):
        name = file.name
        if name.startswith('<') and name.endswith('>'):
            # e.g <fdopen>
            return default
        return name
    return default


def manage_addFile(context, identifier, title=None, file=None):
    """Add a File
    """
    filename = None
    if hasattr(file, 'name'):
        filename = os.path.basename(file.name)
    identifier = mangle.Id(
        context, identifier or filename, file=file, interface=interfaces.IAsset)
    identifier.cook()
    if not identifier.isValid():
        raise ValueError(_(u"Invalid computed identifier."))
    identifier = str(identifier)
    if identifier in context.objectIds():
        raise ValueError(
            _(u"Duplicate id. Please provide an explicit id."))
    service = getUtility(IFilesService)
    context._setObject(identifier, service.new_file(identifier))
    content = context._getOb(identifier)
    if title is not None:
        content.set_title(title)
    if file is not None:
        content.set_file(file)
    notify(ObjectCreatedEvent(content))
    return content


class File(Asset):
    __doc__ = """Any digital file can be uploaded as Silva content.
       For instance large files such as pdf docs or mpegs can be placed in a
       site. File objects have metadata as well."""
    security = ClassSecurityInfo()

    meta_type = "Silva File"

    grok.implements(interfaces.IFile)
    silvaconf.icon('www/silvafile.png')
    silvaconf.factory('manage_addFile')

    # Default values
    _filename = None
    _content_encoding = None

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_filename')
    def get_filename(self):
        """Object's id is filename if not set.
        """
        if self._filename is not None:
            return self._filename
        return self.id

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_file_size')
    def get_file_size(self):
        """Get the size of the file as it will be downloaded.
        """
        return self._file.get_size()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_mime_type')
    def get_mime_type(self):
        """Return the content mimetype.
        """
        # possibly strip out charset encoding
        return self.get_content_type().split(';')[0].strip()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        """Return the content of this object without any markup
        """
        converter = get_converter_for_mimetype(self.get_mime_type())
        fulltext = [self.get_title()]
        if converter is None:
            return fulltext

        text = None
        filename = self.get_file_system_path()
        if filename is not None:
            text = converter.convert_file(filename)
        else:
            file_data = self.get_file()
            if file_data:
                text = converter.convert_string(file_data)
        if text:
            fulltext.append(text)
        return fulltext

    security.declareProtected(
        SilvaPermissions.View, 'get_download_url')
    def get_download_url(self):
        return self.absolute_url()

    security.declareProtected(
        SilvaPermissions.View, 'tag')
    def tag(self, **kw):
        """ return xhtml tag

        Since 'class' is a Python reserved word, it cannot be passed in
        directly in keyword arguments which is a problem if you are
        trying to use 'tag()' to include a CSS class. The tag() method
        will accept a 'css_class' argument that will be converted to
        'class' in the output tag to work around this.
        """
        src = self.get_download_url()
        named = []
        tooltip = unicode(_('download'))

        if kw.has_key('css_class'):
            kw['class'] = kw['css_class']
            del kw['css_class']

        for name, value in kw.items():
            named.append('%s="%s"' % (escape(name), escape(value)))
        named = ' '.join(named)
        return '<a href="%s" title="%s %s" %s>%s</a>' % (
            src, tooltip, self.id, named, self.get_title_or_id())

    # checks where the mime type is text/* or javascript
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_text')
    def is_text(self):
        mimetype = self.get_mime_type()
        if ((mimetype.startswith('text/') and mimetype != 'text/rtf') or
            mimetype in ('application/x-javascript', 'application/xml',
                         'application/xhtml+xml')):
            return self.get_content_encoding() is None
        return False

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_text_editable')
    def is_text_editable(self):
        #size is editable if it is less than 150 KB
        return self.is_text() and (not self.get_file_size() > 153600)

    security.declareProtected(
        SilvaPermissions.View, 'get_text')
    def get_text(self):
        if not self.is_text():
            raise TypeError("Content of Silva File is not text")
        return self.get_file()

    security.declareProtected(
        SilvaPermissions.View, 'get_file')
    def get_file(self):
        fd = self.get_file_fd()
        data = fd.read()
        fd.close()
        return data

    security.declareProtected(
        SilvaPermissions.View, 'get_file_fd')
    def get_file_fd(self):
        raise NotImplementedError

    security.declareProtected(
        SilvaPermissions.View, 'get_content_type')
    def get_content_type(self):
        return self._file.content_type

    security.declareProtected(
        SilvaPermissions.View, 'get_content_encoding')
    def get_content_encoding(self):
        return self._content_encoding

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file')
    def set_file(self, file):
        """Set data in _file object
        """
        self._p_changed = 1
        self._set_file_helper(file)
        if not interfaces.IImage.providedBy(aq_parent(self)):
            # If we are not a storage of an image, trigger an event.
            notify(ObjectModifiedEvent(self))

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_filename')
    def set_filename(self, filename):
        """Set filename
        """
        self._filename = filename

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_file_system_path')
    def get_file_system_path(self):
        """Return path on filesystem for containing File.
        """
        return None

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_content_type')
    def set_content_type(self, content_type):
        self._file.content_type = content_type

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_content_encoding')
    def set_content_encoding(self, content_encoding):
        self._content_encoding = content_encoding

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_text')
    def set_text(self, datastr):
        ct = self._file.content_type
        datafile = StringIO()
        datafile.write(datastr)
        self.set_file(datafile)
        datafile.close()
        self._file.content_type = ct

InitializeClass(File)


class ZODBFile(File):
    """Silva File object, storage in Filesystem. Contains the
    OFS.Image.File.
    """
    grok.implements(interfaces.IZODBFile)
    grok.baseclass()
    security = ClassSecurityInfo()

    def __init__(self, id):
        super(ZODBFile, self).__init__(id)
        # Actual container of file data
        self._file = Image.File(id, id, '')

    def _set_file_helper(self, file):
        data, size = self._file._read_data(file)
        filename = get_file_name(file, default=self.id)
        content_type, content_encoding = getUtility(
            IMimeTypeClassifier).guess_type(
            id=filename,
            buffer=hasattr(data, 'data') and data.data or data,
            default=DEFAULT_MIMETYPE)
        self._file.update_data(data, content_type, size)
        if self._file.content_type == 'text/plain':
            self._file.content_type = 'text/plain; charset=utf-8'
        self._content_encoding = content_encoding

    security.declareProtected(
        SilvaPermissions.View, 'get_file')
    def get_file(self):
        data = self._file.data
        if isinstance(data, StringTypes):
            return data
        return str(data)

    security.declareProtected(
        SilvaPermissions.View, 'get_file_fd')
    def get_file_fd(self):
        return StringIO(self.get_file())

InitializeClass(ZODBFile)


class BlobFile(File):
    """Silva File object, storage using blobs.
    """
    grok.implements(interfaces.IBlobFile)
    grok.baseclass()
    security = ClassSecurityInfo()

    def __init__(self, id):
        super(BlobFile, self).__init__(id)
        self._file = blob.Blob()
        self._content_type = DEFAULT_MIMETYPE

    def _set_content_type(self, file, content_type=None):
        id = get_file_name(file, default=self.id)
        blob_filename = self._file._p_blob_uncommitted or \
            self._file._p_blob_committed
        self._content_type, self._content_encoding = getUtility(
            IMimeTypeClassifier).guess_type(
            id=id,
            filename=blob_filename,
            default=content_type)
        if self._content_type == 'text/plain':
            self._content_type = 'text/plain; charset=utf-8'

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file')
    def set_file(self, file):
        desc = self._file.open('w')
        try:
            data = file.read(CHUNK_SIZE)
            while data:
                desc.write(data)
                data = file.read(CHUNK_SIZE)
        finally:
            desc.close()
        self._set_content_type(file, DEFAULT_MIMETYPE)
        notify(ObjectModifiedEvent(self))

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_text')
    def set_text(self, filestr):
        desc = self._file.open('w')
        desc.write(filestr)
        desc.close()
        notify(ObjectModifiedEvent(self))

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_content_type')
    def set_content_type(self, content_type):
        self._content_type = content_type

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_file_size')
    def get_file_size(self):
        """Get the size of the file as it will be downloaded.
        """
        desc = self._file.open()
        desc.seek(0, 2)
        size = desc.tell()
        desc.close()
        return size

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_content_type')
    def get_content_type(self):
        """Return the content type
        """
        return self._content_type

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_file_fd')
    def get_file_fd(self):
        return self._file.open()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_file_system_path')
    def get_file_system_path(self):
        desc = self._file.open()
        filename = desc.name
        desc.close()
        return filename


InitializeClass(BlobFile)


@grok.subscribe(
    interfaces.IFile, zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def file_modified(content, event):
    getUtility(IMimeTypeClassifier).guess_filename(content, content.getId())
    content.update_quota()


@grok.subscribe(
    interfaces.IFile, zope.lifecycleevent.interfaces.IObjectMovedEvent)
def file_added(content, event):
    if content is not event.object or event.newName is None:
        return
    getUtility(IMimeTypeClassifier).guess_filename(content, event.newName)
