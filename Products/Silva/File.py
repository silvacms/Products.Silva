# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import os
import logging
from types import StringTypes
from cgi import escape
from cStringIO import StringIO

logger = logging.getLogger('silva.file')

# Zope 3
from ZODB import blob
from five import grok
from zope import component
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.datetime import time as time_from_datetime
from zope.event import notify
from zope.interface import directlyProvides
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.location.interfaces import ISite
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
import zope.container.interfaces
import zope.lifecycleevent.interfaces

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from App.class_init import InitializeClass
from webdav.common import rfc1123_date
from ZPublisher.Iterators import IStreamIterator

# Silva
from Products.Silva import mangle
from Products.Silva import SilvaPermissions
from Products.Silva.Asset import Asset
from Products.Silva.ContentObjectFactoryRegistry import \
    contentObjectFactoryRegistry
from Products.Silva.Image import ImageStorageConverter
from Products.Silva.helpers import fix_content_type_header
from Products.Silva.helpers import create_new_filename
from Products.Silva.converters import get_converter_for_mimetype

# Storages
from OFS import Image                            # For ZODB storage
try:                                             #
    from Products.ExtFile.ExtFile import ExtFile # For Filesystem storage;
    FILESYSTEM_STORAGE_AVAILABLE = 1             # try to see if it is
except:                                          # available for import
    FILESYSTEM_STORAGE_AVAILABLE = 0             #

from Products.Silva.magic import MagicGuess

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.conf.interfaces import ITitledContent
from silva.core.conf import schema as silvaschema
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ICataloging
from silva.core.upgrade import upgrade
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.translations import translate as _

from zeam.form import silva as silvaforms
from zeam.form.base import NO_VALUE



CHUNK_SIZE = 1<<16              # 64K
DEFAULT_MIMETYPE = 'application/octet-stream'
MAGIC = MagicGuess()


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
            'Content-Type', self.context.content_type())
        if self.context.content_encoding():
            self.response.setHeader(
                'Content-Encoding', self.context.content_encoding())
        self.response.setHeader(
            'Content-Length', self.context.get_file_size())
        self.response.setHeader(
            'Last-Modified',
            rfc1123_date(self.context.get_modification_datetime()))
        self.response.setHeader(
            'Accept-Ranges', None)


def manage_addFile(context, id, title=None, file=None):
    """Add a File
    """

    content = file_factory(context, id, DEFAULT_MIMETYPE, file)
    if content is None:
        raise ValueError(_(u"Invalid computed identifier."))
    id = content.getId()
    if id in context.objectIds():
        raise ValueError(
            _(u"Duplicate id. Please provide an explicit id."))
    context._setObject(id, content)
    content = getattr(context, id)
    if title:
        content.set_title(title)
    notify(ObjectCreatedEvent(content))
    if file:
        content.set_file_data(file)
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
        return self.content_type().split(';')[0].strip()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        """Return the content of this object without any markup
        """

        mimetype = self.get_mime_type()
        converter = get_converter_for_mimetype(mimetype)
        fulltextlist = [self.get_title()]
        if converter is None:
            return fulltextlist

        file_data = self.get_content()
        fulltext = None
        if file_data:
            fulltext = converter.convert(file_data, self.REQUEST)

        if fulltext is None:
            return fulltextlist
        fulltextlist.append(fulltext)
        return fulltextlist

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
        SilvaPermissions.AccessContentsInformation, 'can_edit_text')
    def can_edit_text(self):
        mt = self.get_mime_type()
        if ((mt.startswith('text/') and mt != 'text/rtf') or \
                mt in ('application/x-javascript',)):
            return True

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_editable_size')
    def is_editable_size(self):
        #size is editable if it is less than 150 KB
        return not self.get_file_size() > 153600

    security.declareProtected(
        SilvaPermissions.View, 'get_text_content')
    def get_text_content(self):
        if not self.can_edit_text():
            raise TypeError("Content of Silva File is not text")
        return self.get_content()

    security.declareProtected(
        SilvaPermissions.View, 'get_content')
    def get_content(self):
        fd = self.get_content_fd()
        data = fd.read()
        fd.close()
        return data

    security.declareProtected(
        SilvaPermissions.View, 'get_content_fd')
    def get_content_fd(self):
        raise NotImplementedError

    security.declareProtected(
        SilvaPermissions.View, 'content_type')
    def content_type(self):
        return self._file.content_type

    security.declareProtected(
        SilvaPermissions.View, 'content_encoding')
    def content_encoding(self):
        return self._content_encoding

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file_data')
    def set_file_data(self, file):
        """Set data in _file object
        """
        self._p_changed = 1
        self._set_file_data_helper(file)
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
        SilvaPermissions.ChangeSilvaContent, 'set_text_file_data')
    def set_text_file_data(self, datastr):
        ct = self._file.content_type
        datafile = StringIO()
        datafile.write(datastr)
        self.set_file_data(datafile)
        datafile.close()
        self._file.content_type = ct

InitializeClass(File)


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

    def _set_file_data_helper(self, file):
        data, size = self._file._read_data(file)
        filename = getattr(file, 'filename', self.id)
        content_type, content_encoding = MAGIC.guess(
            id=filename,
            buffer=hasattr(data, 'data') and data.data or data,
            default=DEFAULT_MIMETYPE)
        self._file.update_data(data, content_type, size)
        if self._file.content_type == 'text/plain':
            self._file.content_type = 'text/plain; charset=utf-8'
        self._content_encoding = content_encoding

    security.declareProtected(
        SilvaPermissions.View, 'get_content')
    def get_content(self):
        data = self._file.data
        if isinstance(data, StringTypes):
            return data
        return str(data)

    security.declareProtected(
        SilvaPermissions.View, 'get_content_fd')
    def get_content_fd(self):
        return StringIO(self.get_content())

InitializeClass(ZODBFile)


class ZODBFileView(silvaviews.View):
    """Download a ZODBFile
    """
    grok.context(ZODBFile)
    grok.require('zope2.View')
    grok.name('index.html')

    def render(self):
        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (self.context.get_filename()))
        return self.context._file.index_html(self.request, self.response)


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
        id  = getattr(file, 'filename', self.id)
        blob_filename = self._file._p_blob_uncommitted or \
            self._file._p_blob_committed
        self._content_type, self._content_encoding = MAGIC.guess(
            id=id,
            filename=blob_filename,
            default=content_type)
        if self._content_type == 'text/plain':
            self._content_type = 'text/plain; charset=utf-8'

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file_data')
    def set_file_data(self, file):
        desc = self._file.open('w')
        data = file.read(CHUNK_SIZE)
        while data:
            desc.write(data)
            data = file.read(CHUNK_SIZE)
        desc.close()
        self._set_content_type(file, DEFAULT_MIMETYPE)
        notify(ObjectModifiedEvent(self))

        #XXX should be event below
        ICataloging(self).reindex()
        self.update_quota()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_text_file_data')
    def set_text_file_data(self, filestr):
        desc = self._file.open('w')
        desc.write(filestr)
        desc.close()
        notify(ObjectModifiedEvent(self))

        #XXX should be event below
        ICataloging(self).reindex()
        self.update_quota()

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
        SilvaPermissions.AccessContentsInformation, 'content_type')
    def content_type(self):
        """
        """
        return self._content_type

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_text_content')
    def get_content_fd(self):
        return self._file.open()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_file_system_path')
    def get_file_system_path(self):
        desc = self._file.open()
        filename = desc.name
        desc.close()
        return filename


InitializeClass(BlobFile)

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
        return FDIterator(self.context.get_content_fd())


class FileSystemFile(File):
    """Silva File object, storage in ZODB. Contains the ExtFile object
    from the ExtFile Product - if available.
    """
    grok.implements(interfaces.IFileSystemFile)
    grok.baseclass()
    security = ClassSecurityInfo()

    def __init__(self, id):
        super(FileSystemFile, self).__init__(id)
        self._file = ExtFile(id, redirect_default_view=1)

    def _get_filename(self):
        path = self._file.get_filename()
        if not os.path.isfile(path):
            path += '.tmp'
        return path

    def _set_file_data_helper(self, file):
        # XXX fix that's
        fix_content_type_header(file)
        self._file.manage_file_upload(file=file)
        if self._file.content_type == 'text/plain':
            self._file.content_type = 'text/plain; charset=utf-8'

    security.declareProtected(
        SilvaPermissions.View, 'get_content_fd')
    def get_content_fd(self):
        return open(self._get_filename(), 'rb')

    security.declareProtected(
        SilvaPermissions.View, 'get_download_url')
    def get_download_url(self):
        return self._file.static_url()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_file_system_path')
    def get_file_system_path(self):
        """return path on filesystem for containing image"""
        # full path from /:
        return self._file.get_filename()

InitializeClass(FileSystemFile)


class FileSystemFileView(silvaviews.View):
    grok.context(FileSystemFile)
    grok.require('zope2.View')
    grok.name('index.html')

    def render(self):
        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (self.context.get_filename()))
        return self.context._file.index_html(
            REQUEST=self.request, RESPONSE=self.response)


def FileStorageTypeVocabulary(context):
    terms = [SimpleTerm(value=ZODBFile, title='ZODB File', token='ZODBFile'),
             SimpleTerm(value=BlobFile, title='Blob File', token='BlobFile'),]
    if FILESYSTEM_STORAGE_AVAILABLE:
        terms += [SimpleTerm(value=FileSystemFile,
                             title='FileSystem File (Legacy)',
                             token='FileSystemFile'),]
    return SimpleVocabulary(terms)

directlyProvides(FileStorageTypeVocabulary, IVocabularyFactory)


class IFileAddSchema(ITitledContent):

    file = silvaschema.Bytes(title=_(u"file"), required=True)


class FileAddForm(silvaforms.SMIAddForm):
    """Add form for a file.
    """
    grok.context(interfaces.IFile)
    grok.name(u'Silva File')

    fields = silvaforms.Fields(IFileAddSchema)
    fields['id'].required = False
    fields['title'].required = False

    def _add(self, parent, data):
        default_id = data['id'] is not NO_VALUE and data['id'] or u''
        default_title = data['title'] is not NO_VALUE and data['title'] or u''
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addFile(
            default_id, default_title, data['file'])


def file_factory(self, id, content_type, file):
    """Create a File.
    """

    id = mangle.Id(self, id, file=file, interface=interfaces.IAsset)
    id.cook()
    if not id.isValid():
        return None
    service_files = component.getUtility(interfaces.IFilesService)
    return service_files.new_file(str(id))


class FilesService(SilvaService):
    meta_type = 'Silva Files Service'
    default_service_identifier = 'service_files'
    silvaconf.icon('www/files_service.gif')

    grok.implements(interfaces.IFilesService)
    security = ClassSecurityInfo()

    storage = FieldProperty(interfaces.IFilesService['storage'])

    manage_options = (
        {'label':'Settings', 'action':'manage_settings'},
        ) + SilvaService.manage_options

    security.declarePrivate('new_file')
    def new_file(self, id):
        if self.storage is None:
            return ZODBFile(id)
        return self.storage(id)

    def is_file_using_correct_storage(self, content):
        storage = ZODBFile
        if self.storage is not None:
            storage = self.storage
        return isinstance(content, storage)


InitializeClass(FilesService)


class FileServiceManagementView(silvaforms.ZMIComposedForm):
    """Edit File Serivce.
    """
    grok.require('zope2.ViewManagementScreens')
    grok.name('manage_settings')
    grok.context(FilesService)

    label = _(u"Configure file storage")


class FileServiceSettings(silvaforms.ZMISubForm):
    grok.context(FilesService)
    silvaforms.view(FileServiceManagementView)
    silvaforms.order(10)

    label = _(u"Select storage")
    fields = silvaforms.Fields(interfaces.IFilesService)
    actions = silvaforms.Actions(silvaforms.EditAction())
    ignoreContent = False


class FileServiceConvert(silvaforms.ZMISubForm):
    grok.context(FilesService)
    silvaforms.view(FileServiceManagementView)
    silvaforms.order(20)

    label = _(u"Convert stored files")
    description = _(u"Convert all currently stored file to "
                    u"the current set storage")

    @silvaforms.action(_(u'Convert all files'))
    def convert(self):
        parent = self.context.get_publication()
        service = self.context
        upg = upgrade.UpgradeRegistry()
        upg.registerUpgrader(
            StorageConverterHelper(parent), '0.1', upgrade.AnyMetaType)
        upg.registerUpgrader(
            FileStorageConverter(service), '0.1', 'Silva File')
        upg.registerUpgrader(
            ImageStorageConverter(service), '0.1', 'Silva Image')
        upg.upgradeTree(parent, '0.1')
        self.status = _(u'Storage for Silva Files and Images converted. '
                        u'Check the log for more details.')


class StorageConverterHelper(object):
    """The purpose of this converter is to stop convertion if there is
    an another configuration.
    """
    grok.implements(interfaces.IUpgrader)

    def __init__(self, publication):
        self.startpoint = publication

    def validate(self, context):
        if context is self.startpoint:
            return False

        if ISite.providedBy(context):
            for obj in context.objectValues():
                if interfaces.IFilesService.providedBy(obj):
                    raise StopIteration()
        return False

    def upgrade(self, context):
        return context


class FileStorageConverter(object):
    """Convert storage for a file.
    """
    grok.implements(interfaces.IUpgrader)

    def __init__(self, service):
        self.service = service

    def validate(self, content):
        if not interfaces.IFile.providedBy(content):
            return False
        if self.service.is_file_using_correct_storage(content):
            # don't convert that are already correct
            return False
        return True

    def upgrade(self, content):
        data = content.get_content_fd()
        id = content.getId()
        title = content.get_title()
        content_type = content.content_type()
        content_encoding = content.content_encoding()

        new_file = self.service.new_file(id)
        container = content.aq_parent
        setattr(container, id, new_file)
        new_file = getattr(container, id)
        new_file.set_title(title)
        new_file.set_file_data(data)
        new_file.set_content_type(content_type)
        new_file.set_content_encoding(content_encoding)

        logger.info("File %s migrated" %
                    '/'.join(new_file.getPhysicalPath()))
        return new_file


contentObjectFactoryRegistry.registerFactory(
    file_factory,
    lambda id, ct, body: True,
    -1)


@grok.subscribe(
    interfaces.IFile, zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def file_changed(file, event):
    create_new_filename(file, file.getId())
    file.update_quota()
    ICataloging(file).reindex()


@grok.subscribe(
    interfaces.IFile, zope.container.interfaces.IObjectMovedEvent)
def file_added(file, event):
    if file is not event.object or event.newName is None:
        return
    create_new_filename(file, event.newName)
