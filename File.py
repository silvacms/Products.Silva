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
from zope import component, schema
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements, Interface, directlyProvides
from zope.location.interfaces import ISite
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.interfaces import IObjectWillBeRemovedEvent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from webdav.common import rfc1123_date
from ZPublisher.Iterators import IStreamIterator

# Silva
from Products.Silva import mangle
from Products.Silva import SilvaPermissions
from Products.Silva.Asset import Asset
from Products.Silva.ContentObjectFactoryRegistry import \
    contentObjectFactoryRegistry
from Products.Silva.Image import ImageStorageConverter
from Products.Silva.helpers import add_and_edit, fix_content_type_header, \
    register_service, unregister_service
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
from silva.core.conf import schema as silvaschema
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ICataloging
from silva.core.upgrade import upgrade
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.core.views import z3cforms as silvaz3cforms
from silva.translations import translate as _
from z3c.form import field


CHUNK_SIZE = 4092
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
    grok.adapts(interfaces.IFile, IBrowserRequest)

    def other_headers(self, headers):
        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (self.context.get_filename()))
        self.response.setHeader(
            'Content-Type', self.context.content_type())
        self.response.setHeader(
            'Content-Length', self.context.get_file_size())
        self.response.setHeader(
            'Last-Modified',
            rfc1123_date(self.context.get_modification_datetime()))
        self.response.setHeader(
            'Accept-Ranges', None)


def manage_addFile(self, id, title=None, file=None):
    """Add a File
    """

    file_obj = file_factory(self, id, DEFAULT_MIMETYPE, file)
    if file_obj is None:
        return None
    id = file_obj.id
    self._setObject(id, file_obj)
    file_obj = getattr(self, id)
    if file:
        file_obj.set_file_data(file)
    if title:
        file_obj.set_title(title)
    return file_obj


class File(Asset):
    __doc__ = """Any digital file can be uploaded as Silva content.
       For instance large files such as pdf docs or mpegs can be placed in a
       site. File objects have metadata as well."""
    security = ClassSecurityInfo()

    meta_type = "Silva File"

    implements(interfaces.IFile)

    silvaconf.priority(-3)
    silvaconf.icon('www/silvafile.png')
    silvaconf.factory('manage_addFile')

    # Default values
    _filename = None

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
        """
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


    def is_editable_size(self):
        #size is editable if it is less than 150 KB
        return not self.get_file_size() > 153600

    def get_text_content(self):
        if not self.can_edit_text():
            raise TypeError("Content of Silva File is not text")
        return self.get_content()

    def get_content(self):
        fd = self.get_content_fd()
        data = fd.read()
        fd.close()
        return data

    def get_content_fd(self):
        raise NotImplementedError

    def content_type(self):
        return self._file.content_type

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file_data')
    def set_file_data(self, file):
        """Set data in _file object
        """
        self._p_changed = 1
        self._set_file_data_helper(file)
        #XXX should be event below
        ICataloging(self).reindex()
        self.update_quota()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_filename')
    def set_filename(self, filename):
        """Set filename
        """
        self._filename = filename

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'getFileSystemPath')
    def getFileSystemPath(self):
        """Return path on filesystem for containing File"""
        return None

    # checks where the mime type is text/* or javascript
    def can_edit_text(self):
        mt = self.get_mime_type()
        if ((mt.startswith('text/') and mt != 'text/rtf') or \
                mt in ('application/x-javascript',)):
            return True

    def set_content_type(self, content_type):
        self._file.content_type = content_type

    def set_text_file_data(self, datastr):
        ct = self._file.content_type
        datafile = StringIO()
        datafile.write(datastr)
        self.set_file_data(datafile)
        datafile.close()
        self._file.content_type = ct

InitializeClass(File)


class ZODBFile(File):
    """Silva File object, storage in Filesystem. Contains the OFS.Image.File
    """

    implements(interfaces.IZODBFile)

    silvaconf.baseclass()

    def __init__(self, id):
        super(ZODBFile, self).__init__(id)
        # Actual container of file data
        self._file = Image.File(id, id, '')

    def _set_file_data_helper(self, file):
        data, size = self._file._read_data(file)
        filename = getattr(file, 'filename', self.id)
        content_type = MAGIC.guess(
            id=filename,
            buffer=hasattr(data, 'data') and data.data or data,
            default=DEFAULT_MIMETYPE)
        self._file.update_data(data, content_type, size)
        if self._file.content_type == 'text/plain':
            self._file.content_type = 'text/plain; charset=utf-8'

    def get_content(self):
        data = self._file.data
        if isinstance(data, StringTypes):
            return data
        return str(data)

    def get_content_fd(self):
        return StringIO(self.get_content())

InitializeClass(ZODBFile)


class ZODBFileView(silvaviews.View):

    silvaconf.context(ZODBFile)
    silvaconf.require('zope2.View')
    silvaconf.name('index')

    def render(self):
        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (self.context.get_filename()))
        return self.context._file.index_html(self.request, self.response)


class BlobFile(File):
    """Silva File object, storage using blobs.
    """

    implements(interfaces.IBlobFile)

    silvaconf.baseclass()
    security = ClassSecurityInfo()

    def __init__(self, id):
        super(BlobFile, self).__init__(id)
        self._file = blob.Blob()
        self._content_type = DEFAULT_MIMETYPE

    def _set_content_type(self, file, content_type=None):
        id  = getattr(file, 'filename', self.id)
        blob_filename = self._file._p_blob_uncommitted or \
            self._file._p_blob_committed
        self._content_type = MAGIC.guess(
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
        #XXX should be event below
        ICataloging(self).reindex()
        self.update_quota()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_text_file_data')
    def set_text_file_data(self, filestr):
        desc = self._file.open('w')
        desc.write(filestr)
        desc.close()
        #XXX should be event below
        ICataloging(self).reindex()
        self.update_quota()

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


InitializeClass(BlobFile)

class BlobFileView(silvaviews.View):

    silvaconf.context(BlobFile)
    silvaconf.require('zope2.View')
    silvaconf.name('index')

    def render(self):
        return FDIterator(self.context.get_content_fd())


class FileSystemFile(File):
    """Silva File object, storage in ZODB. Contains the ExtFile object
    from the ExtFile Product - if available.
    """

    implements(interfaces.IFileSystemFile)

    silvaconf.baseclass()
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

    def get_content_fd(self):
        return open(self._get_filename(), 'rb')

    security.declareProtected(
        SilvaPermissions.View, 'get_download_url')
    def get_download_url(self):
        return self._file.static_url()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'getFileSystemPath')
    def getFileSystemPath(self):
        """return path on filesystem for containing image"""
        # full path from /:
        return self._file.get_filename()

InitializeClass(FileSystemFile)


class FileSystemFileView(silvaviews.View):

    silvaconf.context(FileSystemFile)
    silvaconf.require('zope2.View')
    silvaconf.name('index')

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
                             title='FileSystem File',
                             token='FileSystemFile'),]
    return SimpleVocabulary(terms)

directlyProvides(FileStorageTypeVocabulary, IVocabularyFactory)


class IFileAddFields(Interface):

    file = silvaschema.Bytes(title=_(u"file"), required=True)
    id = silvaschema.ID(
        title=_(u"id"),
        description=_(u"No spaces or special characters besides ‘_’ or ‘-’ or ‘.’"),
        required=False)
    title = schema.TextLine(
        title=_(u"title"),
        description=_(u"Tip: You don't have to fill in the id and title."),
        required=False)


class FileAddForm(silvaz3cforms.AddForm):
    """Add form for a file.
    """

    silvaconf.context(interfaces.IFile)
    silvaconf.name(u'Silva File')
    fields = field.Fields(IFileAddFields)

    def create(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addFile(
            data['id'], data['title'], data['file'])


def file_factory(self, id, content_type, file):
    """Create a File.
    """

    id = mangle.Id(self, id, file=file, interface=interfaces.IAsset)
    id.cook()
    if not id.isValid():
        return None
    service_files = component.getUtility(interfaces.IFilesService)
    return service_files.newFile(str(id))


class FilesService(SilvaService):
    meta_type = 'Silva Files Service'
    silvaconf.icon('www/files_service.gif')
    silvaconf.factory('manage_addFilesServiceForm')
    silvaconf.factory('manage_addFilesService')

    implements(interfaces.IFilesService)
    security = ClassSecurityInfo()

    storage = FieldProperty(interfaces.IFilesService['storage'])

    manage_options = (
        {'label':'Edit', 'action':'manage_filesservice'},
        ) + SilvaService.manage_options

    security.declarePrivate('newFile')
    def newFile(self, id):
        if self.storage is None:
            return ZODBFile(id)
        return self.storage(id)


InitializeClass(FilesService)


manage_addFilesServiceForm = PageTemplateFile(
    "www/filesServiceAdd", globals(),
    __name__='manage_addFilesServiceForm')


from zope.formlib import form

class FileServiceManagementView(silvaviews.ZMIEditForm):

    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.name('manage_filesservice')
    silvaconf.context(FilesService)

    form_fields = grok.Fields(interfaces.IFilesService)
    actions =  form.Actions(silvaviews.ZMIEditForm.handle_edit_action,
        form.Action('Convert all files', success='action_convert'))

    def convert(self):
        parent = self.context.get_publication()
        upg = upgrade.UpgradeRegistry()
        upg.registerUpgrader(
            StorageConverterHelper(parent), '0.1', upgrade.AnyMetaType)
        upg.registerUpgrader(FileStorageConverter(), '0.1', 'Silva File')
        upg.registerUpgrader(ImageStorageConverter(), '0.1', 'Silva Image')
        upg.upgradeTree(parent, '0.1')

    def action_convert(self, action, data):
        self.convert()
        self.status = u'Silva Files and Images converted. ' \
            u'See Zope log for details.'


class StorageConverterHelper(object):
    """The purpose of this converter is to stop convertion if there is
    an another configuration.
    """

    implements(interfaces.IUpgrader)

    def __init__(self, publication):
        self.startpoint = publication

    def upgrade(self, context):
        if context is self.startpoint:
            return context

        if ISite.providedBy(context):
            for obj in context.objectValues():
                if interfaces.IFilesService.providedBy(obj):
                    dummy = ConversionBlocker()
                    dummy.aq_base = ConversionBlocker()
                    return dummy
        return context


class ConversionBlocker(object):
    pass


class FileStorageConverter(object):

    implements(interfaces.IUpgrader)

    def upgrade(self, old_file):
        if not interfaces.IFile.providedBy(old_file):
            return old_file
        data = old_file.get_content_fd()
        id = old_file.id
        title = old_file.get_title()
        content_type = old_file.content_type()

        new_file = old_file.service_files.newFile(id)
        container = old_file.aq_parent
        setattr(container, id, new_file)
        new_file = getattr(container, id)
        new_file.set_title(title)
        new_file.set_file_data(data)
        new_file.set_content_type(content_type)

        logger.info("File %s migrated" %
                    '/'.join(new_file.getPhysicalPath()))
        return new_file


def manage_addFilesService(self, id, title=None, REQUEST=None):
    """Add files service.
    """
    if title is None:
        title = id
    service = FilesService(id, title)
    register_service(self, id, service, interfaces.IFilesService)
    add_and_edit(self, id, REQUEST)
    return ''


@silvaconf.subscribe(interfaces.IFilesService, IObjectWillBeRemovedEvent)
def unregisterFileService(service, event):
    unregister_service(service, interfaces.IFilesService)


contentObjectFactoryRegistry.registerFactory(
    file_factory,
    lambda id, ct, body: True,
    -1)
