# -*- coding: iso-8859-1 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.44 $

from zope.interface import implements
# Python
import os
import string
from cgi import escape
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
# Zope
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from mimetypes import guess_extension
from helpers import add_and_edit, fix_content_type_header
from webdav.WriteLockInterface import WriteLockInterface
import zLOG
# Silva
from Asset import Asset
from Products.Silva import mangle
from Products.Silva import SilvaPermissions
from Products.Silva import upgrade
from Products.Silva.i18n import translate as _
from Products.Silva.ContentObjectFactoryRegistry import \
        contentObjectFactoryRegistry
# Storages
from OFS import Image                            # For ZODB storage
try:                                             #
    from Products.ExtFile.ExtFile import ExtFile # For Filesystem storage;
    FILESYSTEM_STORAGE_AVAILABLE = 1             # try to see if it is 
except:                                          # available for import
    FILESYSTEM_STORAGE_AVAILABLE = 0             #

from Products.Silva.adapters.interfaces import IAssetData
from interfaces import IFile, IAsset, IUpgrader

icon="www/silvafile.png"
addable_priority = -0.3

class File(Asset):
    __doc__ = _("""Any digital file can be uploaded as Silva content. 
       For instance large files such as pdf docs or mpegs can be placed in a
       site. File objects have metadata as well. 
       <!-- Abstract base class. Depends on a _file attribute and various 
       methods in the concrete subclasses. (sorry) -->
    """)
    security = ClassSecurityInfo()
    
    meta_type = "Silva File"

    __implements__ = (WriteLockInterface,)
    implements(IFile)
    
    def __init__(self, id, title):
        File.inheritedAttribute('__init__')(self, id, title)

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_filename')
    def get_filename(self):
        """Object's id is filename
        """
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
        return self._file.content_type

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_download_url')
    # XXX deprecated, method left for backwards compatibility
    def get_download_url(self):
        """Obtain the public URL the public could use to download this file
        """
        # XXX print deprecated warning?
        return self.absolute_url()

    # Overide SilvaObject.to_xml().
    security.declareProtected(SilvaPermissions.ReadSilvaContent, 'to_xml')
    def to_xml(self, context):
        """Overide from SilvaObject
        """
        context.f.write(
            '<file id="%s" url=%s>%s</file>' % (
            self.id, self.get_download_url(), self._title))

    security.declareProtected(SilvaPermissions.View, 'index_html')
    def index_html(self, view_method=None):
        """ view (download) file data
        
        view_method: parameter is set by preview_html (for instance) but
        ignored here.
        """
        request = self.REQUEST
        request.RESPONSE.setHeader(
            'Content-Disposition', 'inline;filename=%s' % (self.get_filename()))
        return self._index_html_helper(request)
    
    security.declareProtected(SilvaPermissions.View, 'download')
    # XXX deprecated, method left for backwards compatibility
    def download(self, *args, **kw):
        """ view (download) file data.
        """
        # XXX print deprecated warning?
        return self.index_html(*args, **kw)

    security.declareProtected(SilvaPermissions.View, 'tag')
    def tag(self, **kw):
        """ return xhtml tag
        
        Since 'class' is a Python reserved word, it cannot be passed in
        directly in keyword arguments which is a problem if you are
        trying to use 'tag()' to include a CSS class. The tag() method
        will accept a 'css_class' argument that will be converted to
        'class' in the output tag to work around this.
        """
        src = self.absolute_url()
        title = self.get_title_or_id()
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
    
    security.declareProtected(SilvaPermissions.View, 'get_download_link')
    # XXX deprecated, method left for backwards compatibility
    def get_download_link(self, *args, **kw):
        # XXX print deprecated warning?
        return self.tag(*args, **kw)
    
    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file_data')
    def set_file_data(self, file):
        """Set data in _file object
        """
        self._p_changed = 1
        self._set_file_data_helper(file)        

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
        'getFileSystemPath')
    def getFileSystemPath(self):
        """return path on filesystem for containing image"""
        f = self._file
        if isinstance(f, Image.File):
            return None
        # full path from /:
        return f.get_filename()
        # this would be relative to repository:
        return '/'.join(f.filename)

    def manage_FTPget(self, *args, **kwargs):
        return self._file.manage_FTPget(*args, **kwargs)

    def content_type(self):
        return self._file.content_type

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests"""
        return self._file.PUT(REQUEST, RESPONSE)

    def HEAD(self, REQUEST, RESPONSE):
        """ forward the request to the underlying file object
        """
        # should this set the content-disposition header,
        # like the "index_html" does?
        return self._file.HEAD(REQUEST, RESPONSE)

InitializeClass(File)


class ZODBFile(File):                                   
    """Silva File object, storage in Filesystem. Contains the OFS.Image.File
    """       
    def __init__(self, id, title):
        ZODBFile.inheritedAttribute('__init__')(self, id, title)
        # Actual container of file data
        self._file = Image.File(id, title, '')        

    def _set_file_data_helper(self, file):
        # ensure consistent mimetype assignment by deleting content-type header
        fix_content_type_header(file)
        self._file.manage_upload(file=file)

    def _index_html_helper(self, REQUEST):
        return self._file.index_html(REQUEST, REQUEST.RESPONSE) # parameters needed for OFS.File

InitializeClass(ZODBFile)


class FileSystemFile(File):
    """Silva File object, storage in ZODB. Contains the ExtFile object
    from the ExtFile Product - if available.
    """    

    def __init__(self, id, title, repository):
        FileSystemFile.inheritedAttribute('__init__')(self, id, title)        
        self._file = ExtFile(id, title)
        self._file._repository = cookPath(repository)

    def _set_file_data_helper(self, file):
        # ensure consistent mimetype assignment by deleting content-type header
        fix_content_type_header(file)
        self._file.manage_file_upload(file=file)

    def _index_html_helper(self, REQUEST):
        return self._file.index_html(REQUEST=REQUEST)

    def manage_beforeDelete(self, item, container):
        FileSystemFile.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self._file.manage_beforeDelete(item, container)

    def manage_afterClone(self, item):
        FileSystemFile.inheritedAttribute('manage_afterClone')(self, item)
        self._file.manage_afterClone(item)

    def manage_afterAdd(self, item, container):
        FileSystemFile.inheritedAttribute('manage_afterAdd')(self, item, container)
        self._file.manage_afterAdd(item, container)

InitializeClass(FileSystemFile)


manage_addFileForm=PageTemplateFile(
    "www/fileAdd", globals(), __name__='manage_addFileForm', Kind='File', kind='file')
# Copy code from ExtFile, but we don't want a dependency per se:
bad_chars =  r""" ,;()[]{}~`'"!@#$%^&*+=|\/<>?ÄÅÁÀÂÃäåáàâãÇçÉÈÊËÆéèêëæÍÌÎÏíìîïÑñÖÓÒÔÕØöóòôõøŠšßÜÚÙÛüúùûÝŸýÿŽž"""
good_chars = r"""_____________________________AAAAAAaaaaaaCcEEEEEeeeeeIIIIiiiiNnOOOOOOooooooSssUUUUuuuuYYyyZz"""
TRANSMAP = string.maketrans(bad_chars, good_chars)

def manage_addFile(self, id, title, file):
    """Add a File
    """
    id = mangle.Id(self, id, file=file, interface=IAsset)
    # try to rewrite the id to make it unique
    id.cook()
    id = str(id)
    # the content type is a formality here, the factory expects
    # it as an arg but doesn't actually use it
    object = file_factory(self, id, 'application/unknown', file)

    self._setObject(id, object)
    object = getattr(self, id)
    object.set_title(title)
    object._set_file_data_helper(file)
    return object

def file_factory(self, id, content_type, file):
    """Add a File
    """
    # if this gets called by the contentObjectFactoryRegistry, the last 
    # argument will be a string
    # XXX is this useful? do we use 'file' at all (what would 'mangle' want
    # with it?)
    if type(file) in (str, unicode):
        f = StringIO()
        f.write(file)
        file = f
    id = mangle.Id(self, id, file=file, interface=IAsset)
    if not id.isValid():
        return 
    id = str(id)

    # Switch storage type:
    service_files = getattr(self, 'service_files', None)
    assert service_files is not None, \
                        ("There is no service_files. "
                            "Refresh your silva root.")
    if service_files.useFSStorage():        
        object = FileSystemFile(id, id, service_files.filesystem_path())
    else:
        object = ZODBFile(id, id)
    return object

class FilesService(SimpleItem.SimpleItem):
    meta_type = 'Silva Files Service'

    security = ClassSecurityInfo()
    
    manage_options = (
        {'label':'Edit', 'action':'manage_filesServiceEditForm'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected('View management screens', 
        'manage_filesServiceEditForm')
    manage_filesServiceEditForm = PageTemplateFile(
        'www/filesServiceEdit', globals(),  
        __name__='manage_filesServiceEditForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_filesServiceEditForm # used by add_and_edit()

    def __init__(self, id, title, filesystem_storage_enabled=0,
            filesystem_path='var/repository'):
        self.id = id
        self.title = title
        self._filesystem_storage_enabled = filesystem_storage_enabled
        self._filesystem_path = filesystem_path

    # ACCESSORS
    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'is_filesystem_storage_available')
    def is_filesystem_storage_available(self):
        """is_filesystem_storage_available
        """
        return FILESYSTEM_STORAGE_AVAILABLE 
    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'filesystem_storage_enabled')
    def filesystem_storage_enabled(self):
        """filesystem_storage_enabled
        """
        return self._filesystem_storage_enabled

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'useFSStorage')
    def useFSStorage(self):
        return (self.is_filesystem_storage_available() and 
            self.filesystem_storage_enabled())
    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'filesystem_path')
    def filesystem_path(self):
        """filesystem_path
        """
        return self._filesystem_path

    security.declarePublic('cookPath')
    def cookPath(self, path):
        "call cook path"
        return cookPath(path)

    # MANIPULATORS
    security.declareProtected('View management screens', 
        'manage_filesServiceEdit')
    def manage_filesServiceEdit(self, title='', filesystem_storage_enabled=0, 
            filesystem_path='', REQUEST=None):
        """Sets storage type/path for this site.
        """
        self.title = title
        self._filesystem_storage_enabled = filesystem_storage_enabled
        self._filesystem_path = filesystem_path
        if REQUEST is not None:
            return self.manage_filesServiceEditForm(
                manage_tabs_message='Settings Changed')

    security.declareProtected(
        'View management screens', 'manage_convertStorage')
    def manage_convertStorage(self, REQUEST=None):
        """converts images and files to be stored like set in files service"""
        from Products.Silva.Image import ImageStorageConverter
        upg = upgrade.UpgradeRegistry()
        upg.registerUpgrader(
            StorageConverterHelper(self.aq_parent), '0.1', upgrade.AnyMetaType)
        upg.registerUpgrader(FileStorageConverter(), '0.1', 'Silva File')
        upg.registerUpgrader(ImageStorageConverter(), '0.1', 'Silva Image')
        upg.upgradeTree(self.aq_parent, '0.1')
        if REQUEST is not None:
            return self.manage_filesServiceEditForm(manage_tabs_message=(
                'Silva Files and Images converted. See Zope log for details.'))

InitializeClass(FilesService)

manage_addFilesServiceForm = PageTemplateFile(
    "www/filesServiceAdd", globals(), __name__='manage_addFilesServiceForm')

class FileStorageConverter:
    
    implements(IUpgrader)
    
    def upgrade(self, context):
        adapted = IAssetData(context)
        # XXX not sure this makes sense after adapter conversion..
        if adapted is None:
            return context
        data = adapted.getData()
        data = StringIO(data)
        id = context.id
        title = context.get_title()
        files_service = context.service_files
        if files_service.useFSStorage():
            fileobject = FileSystemFile(
                id, title, files_service.filesystem_path())
        else:
            fileobject = ZODBFile(id, title)
        del context.__dict__['_file']
        fileobject.__dict__.update(context.__dict__)
        container = context.aq_parent
        setattr(container, id, fileobject)
        fileobject = getattr(container, id)
        fileobject.set_file_data(data)
        zLOG.LOG(
            'Silva', zLOG.INFO, "File %s migrated" % '/'.join(fileobject.getPhysicalPath())) 
        return fileobject

class StorageConverterHelper:
    
    implements(IUpgrader)
    
    def __init__(self, initialcontext):
        self.initialcontext = initialcontext

    def upgrade(self, context):
        if context is self.initialcontext:
            return context
        # Check if context is a container-like object.
        # If the context contains a 'service_files' object
        # return a Dummy which will stop the conversion for
        # this subtree.
        # If not, just return the context to let conversion continue
        if hasattr(context.aq_base, 'objectIds'):
            if 'service_files' in context.objectIds():
                dummy = _dummy()
                dummy.aq_base = _dummy()
                return dummy
        return context
    
class _dummy:
    pass
    
def manage_addFilesService(self, id, title='', filesystem_storage_enabled=0,
        filesystem_path='', REQUEST=None):    
    """Add files service."""
    object = FilesService(id, title, filesystem_storage_enabled,
        filesystem_path)    
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return '' #object.manage_filesServiceEditForm()

def cookPath(path):
    bad_dirs = ['', '.', '..']
    path_items = []
    while 1:
        path, item = os.path.split(path)
        if item not in bad_dirs:
            path_items.append(item)
        if path in ('', '/'):
            break
    path_items.reverse()        
    return tuple(path_items)

contentObjectFactoryRegistry.registerFactory(
    file_factory,
    lambda id, ct, body: True,
    -1)
