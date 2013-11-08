# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from cStringIO import StringIO
from cgi import escape
from types import StringTypes
import logging
import os
import os.path
import time
import warnings

# Zope 3
from ZODB import blob
from five import grok
from zope.component import getUtility, getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from App.class_init import InitializeClass
from OFS import Image   # For ZODB storage

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Asset import Asset
from Products.Silva.File.converters import get_converter_for_mimetype

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.conf.utils import ISilvaFactoryDispatcher
from silva.core.interfaces import ContentError
from silva.core.interfaces import IMimeTypeClassifier, ISilvaNameChooser
from silva.core.services.interfaces import IFilesService
from silva.core.views.interfaces import IContentURL
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

    container = context
    if ISilvaFactoryDispatcher.providedBy(container):
        container = container.Destination()

    chooser = ISilvaNameChooser(container)
    identifier = chooser.chooseName(
        identifier or filename, None, file=file, interface=interfaces.IAsset)
    try:
        chooser.checkName(identifier, None)
    except ContentError as e:
        raise ValueError(_(u"Please provide a unique id: ${reason}",
            mapping=dict(reason=e.reason)))
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
    silvaconf.icon('icons/file.png')
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
    def get_download_url(self, preview=False, request=None):
        if request is None:
            request = self.REQUEST
        url = getMultiAdapter((self, request), IContentURL).url(preview=preview)
        if preview:
            # In case of preview we add something that change at the
            # end of the url to prevent caching from the browser.
            url += '?' + str(int(time.time()))
        return url

    security.declareProtected(
        SilvaPermissions.View, 'tag')
    def tag(self, **kw):
        warnings.warn(
            'tag have been replaced with get_html_tag. '
            'It will be removed, please update your code.',
            DeprecationWarning, stacklevel=2)
        return self.get_html_tag(**kw)

    security.declareProtected(SilvaPermissions.View, 'get_html_tag')
    def get_html_tag(self, preview=False, request=None, **extra_attributes):
        """ return xhtml tag

        Since 'class' is a Python reserved word, it cannot be passed in
        directly in keyword arguments which is a problem if you are
        trying to use 'tag()' to include a CSS class. The tag() method
        will accept a 'css_class' argument that will be converted to
        'class' in the output tag to work around this.
        """
        src = self.get_download_url(preview, request)
        title = self.get_title_or_id()

        if extra_attributes.has_key('css_class'):
            extra_attributes['class'] = extra_attributes['css_class']
            del extra_attributes['css_class']

        extra_html_attributes = [
            u'{name}="{value}"'.format(name=escape(name, 1),
                                      value=escape(value, 1))
            for name, value in extra_attributes.iteritems()]

        return '<a href="%s" title="Download %s" %s>%s</a>' % (
            src, self.get_filename(), extra_html_attributes, title)

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
    def set_file(self, stream, content_type=None, content_encoding=None):
        """Set data in _file object
        """
        raise NotImplementedError

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
    def set_text(self, text):
        raise NotImplementedError

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

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file')
    def set_file(self, stream, content_type=None, content_encoding=None):
        """Set data in _file object
        """
        data, size = self._file._read_data(stream)
        if content_type is None:
            # Detect content-type
            identifier = get_file_name(stream, default=self.id)
            content_type, content_encoding = getUtility(
                IMimeTypeClassifier).guess_type(
                id=identifier,
                buffer=hasattr(data, 'data') and data.data or data,
                default=DEFAULT_MIMETYPE)
        # Update file data.
        self._file.update_data(data, content_type, size)
        if self._file.content_type == 'text/plain':
            self._file.content_type = 'text/plain; charset=utf-8'
        self._content_encoding = content_encoding
        if not interfaces.IImage.providedBy(aq_parent(self)):
        #    # If we are not a storage of an image, trigger an event.
            notify(ObjectModifiedEvent(self))

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_text')
    def set_text(self, text):
        stream = StringIO()
        stream.write(text)
        self.set_file(stream, content_type=self._file.content_type)
        stream.close()

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

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file')
    def set_file(self, stream, content_type=None, content_encoding=None):
        with self._file.open('w') as descriptor:
            data = stream.read(CHUNK_SIZE)
            while data:
                descriptor.write(data)
                data = stream.read(CHUNK_SIZE)
        if content_type is None:
            # Detect content-type
            identifier = get_file_name(stream, default=self.id)
            blob_filename = self._file._p_blob_uncommitted or \
                self._file._p_blob_committed
            self._content_type, self._content_encoding = getUtility(
                IMimeTypeClassifier).guess_type(
                id=identifier,
                filename=blob_filename,
                default=DEFAULT_MIMETYPE)
        else:
            # Set provided values
            self._content_type = content_type
            self._content_encoding = content_encoding
        if self._content_type == 'text/plain':
            self._content_type = 'text/plain; charset=utf-8'
        if not interfaces.IImage.providedBy(aq_parent(self)):
        #    # If we are not a storage of an image, trigger an event.
            notify(ObjectModifiedEvent(self))

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_text')
    def set_text(self, text):
        with self._file.open('w') as descriptor:
            descriptor.write(text)
        if not interfaces.IImage.providedBy(aq_parent(self)):
        #    # If we are not a storage of an image, trigger an event.
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
        with self._file.open() as descriptor:
            descriptor.seek(0, 2)
            return descriptor.tell()

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
        with self._file.open() as descriptor:
            return descriptor.name


InitializeClass(BlobFile)


class FilePayload(grok.Adapter):
    grok.implements(interfaces.IAssetPayload)
    grok.context(interfaces.IFile)

    def get_payload(self):
        return self.context.get_file()


@grok.subscribe(interfaces.IFile, IObjectModifiedEvent)
@grok.subscribe(interfaces.IFile, IObjectCreatedEvent)
def file_modified(content, event):
    getUtility(IMimeTypeClassifier).guess_filename(content, content.getId())


@grok.subscribe(interfaces.IFile, IObjectMovedEvent)
def file_added(content, event):
    if content is not event.object or event.newName is None:
        return
    getUtility(IMimeTypeClassifier).guess_filename(content, event.newName)

