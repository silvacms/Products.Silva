# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6.2.4 $

# Python
import os
import string
# Zope
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from mimetypes import guess_extension
from helpers import add_and_edit
from webdav.WriteLockInterface import WriteLockInterface
# Silva interfaces
from IAsset import IAsset
# Silva
from Asset import Asset
import SilvaPermissions
# Storages
from OFS import Image                            # For ZODB storage
try:                                             #
    from Products.ExtFile.ExtFile import ExtFile # For Filesystem storage;
    FILESYSTEM_STORAGE_AVAILABLE = 1             # try to see if it is 
except:                                          # available for import
    FILESYSTEM_STORAGE_AVAILABLE = 0             #

icon="www/silvafile.png"

class File(Asset):
    """Any digital file can be uploaded as Silva content. 
       For instance large files such as pdf docs or mpegs can be placed in a
       site. File objects have metadata as well. 
       <!-- Abstract base class. Depends on a _file attribute and various 
       methods in the concrete subclasses. (sorry) -->
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva File"    

    __implements__ = (WriteLockInterface, IAsset)

    def __init__(self, id, title):
        File.inheritedAttribute('__init__')(self, id, title)
        # Anticipating hook:
        self._direct_download = 1

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
    def get_download_url(self):
        """Obtain the public URL the public could use to download this file
        """
        return self.absolute_url()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_download_link')
    def get_download_link(
        self, title_attr='', name_attr='', class_attr='', style_attr=''):
        """Obtain a complete HTML hyperlink by which the public can download
        this file. FIXME: Is this method really needed?
        """
        attrs = []
        if title_attr:
            attrs.append('title="%s"' % title_attr)
        if name_attr:
            attrs.append('name="%s"' % name_attr)
        if class_attr:
            attrs.append('class="%s"' % class_attr)
        if style_attr:
            attrs.append('style="%"' % style_attr)
        attrs = ' '.join(attrs)
        link_text = self.get_title_html() or self.id
        return '<a %s href="%s">%s</a>' % (
            attrs, self.get_download_url(), link_text)

    # Overide SilvaObject.to_xml().
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'to_xml')
    def to_xml(self, context):
        """Overide from SilvaObject
        """
        context.f.write(
            '<file id="%s" url=%s>%s</file>' % (
            self.id, self.get_download_url(), self._title))

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'download')
    def download(self, REQUEST):
        """Wrap around _file object
        """
        REQUEST.RESPONSE.setHeader(
            'Content-Disposition', 'inline;filename=%s' % (self.get_filename()))
        return self._index_html_helper(REQUEST)

    # Overide index_html in public presentation templates.
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'index_html')
    def index_html(self, REQUEST=None):
        """Get to file
        """
        if not self._direct_download:
            return self.view()
        return self.download(REQUEST=REQUEST)        

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_file_data')
    def set_file_data(self, file):
        """Set data in _file object
        """
        self._set_file_data_helper(file)
        self._p_changed = 1

    def manage_FTPget(self, *args, **kwargs):
        return self._file.manage_FTPget(*args, **kwargs)

    def content_type(self):
        return self._file.content_type

    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests"""
        return self._file.PUT(REQUEST, RESPONSE)

InitializeClass(File)


class ZODBFile(File):                                   
    """Silva File object, storage in Filesystem. Contains the OFS.Image.File    
    """       
    def __init__(self, id, title, file):
        ZODBFile.inheritedAttribute('__init__')(self, id, title)
        # Actual container of file data
        self._file = Image.File(id, title, '')        
        self._set_file_data_helper(file)

    def _set_file_data_helper(self, file):
        self._file.manage_upload(file=file)

    def _index_html_helper(self, REQUEST):
        return self._file.index_html(REQUEST, REQUEST.RESPONSE) # parameters needed for OFS.File

InitializeClass(ZODBFile)


class FileSystemFile(File):
    """Silva File object, storage in ZODB. Contains the ExtFile object
    from the ExtFile Product - if available.
    """    

    def __init__(self, id, title, file, repository):
        FileSystemFile.inheritedAttribute('__init__')(self, id, title)        
        self._file = ExtFile(id, title)
        self._file._repository = cookPath(repository)
        self._set_file_data_helper(file)

    def _set_file_data_helper(self, file):
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
bad_chars =  r""" ,;()[]{}~`'"!@#$%^&*+=|\/<>?ƒ≈¡¿¬√‰Â·‡‚„«Á…» À∆ÈËÍÎÊÕÃŒœÌÏÓÔ—Ò÷”“‘’ÿˆÛÚÙı¯äöﬂ‹⁄Ÿ€¸˙˘˚›ü˝ˇéû"""
good_chars = r"""_____________________________AAAAAAaaaaaaCcEEEEEeeeeeIIIIiiiiNnOOOOOOooooooSssUUUUuuuuYYyyZz"""
TRANSMAP = string.maketrans(bad_chars, good_chars)

def manage_addFile(self, id='', title='', file=''):
    """Add a File
    """
    id, _title = Image.cookId(id, title, file)
    #    ^
    #    |  
    #    +-- The cooked title is not used for creating file objects.
    
    # Copy code from ExtFile, but we don't want a dependency per se:
    id = string.translate(id, TRANSMAP)

    # Switch storage type:
    service_files = getattr(self.aq_inner, 'service_files', None)
    assert service_files is not None, "There is no service_files. " \
        "Refresh your silva root."
    assert service_files.meta_type == 'Silva Files Service', "Cannot reach "\
        "the files service, a `%s' is in the way" % (service_files.meta_type, )
    if service_files.useFSStorage():        
        object = FileSystemFile(id, title, file, 
            service_files.filesystem_path())
    else:
        object = ZODBFile(id, title, file)
    self._setObject(id, object)
    object = getattr(self, id)
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

    def is_filesystem_storage_available(self):
        """is_filesystem_storage_available
        """
        return FILESYSTEM_STORAGE_AVAILABLE 
    
    def filesystem_storage_enabled(self):
        """filesystem_storage_enabled
        """
        return self._filesystem_storage_enabled

    def useFSStorage(self):
        return (self.is_filesystem_storage_available() and 
            self.filesystem_storage_enabled())

    def filesystem_path(self):
        """filesystem_path
        """
        return self._filesystem_path

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

InitializeClass(FilesService)


manage_addFilesServiceForm = PageTemplateFile(
    "www/filesServiceAdd", globals(), __name__='manage_addFilesServiceForm')

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

