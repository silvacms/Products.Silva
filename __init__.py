# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.45 $
import ViewRegistry, MultiViewRegistry
import Document, Folder, Root
import Publication, Ghost, Image, File
import DemoObject, CatalogedDemoObject, Indexer
import install
from Products.Silva.ImporterRegistry import importer_registry
from ExtensionRegistry import extensionRegistry
import ExtensionService
# enable Formulator support for FileSystemSite
from Products.Formulator import FSForm
# so we can register directories for FileSystemSite
from Products.FileSystemSite.DirectoryView import registerDirectory, registerFileExtension
from Products.FileSystemSite.FSImage import FSImage
# enable .ico support for FileSystemSite
registerFileExtension('ico', FSImage)

# -- monkey patch FileSystemSite's minimalpath until new release --
import os
from os import path as os_path
separators = (os.sep, os.altsep)
def minimalpath(p):
    # Trims down to a 'Products' root if it can.
    # otherwise, it returns what it was given.
    # In either case, the path is normalized.
    p = os_path.abspath(os_path.normcase(os_path.normpath(p)))
    index = p.find('Products')
    if index == -1:
        index = p.find('products')
    if index == -1:
        return p
    p = p[index:]
    while p[:1] in separators:
        p = p[1:]
    return p

from Products import FileSystemSite
FileSystemSite.DirectoryView.minimalpath = minimalpath
FileSystemSite.utils.minimalpath = minimalpath
# -- monkey patch end ---

def initialize(context):
    extensionRegistry.register(
        'Silva', 'Silva Core', context, [
        Document, Folder, Root, Publication, Ghost, Image, File,
        DemoObject, Indexer],
        install, depends_on=None)

    context.registerClass(
        ViewRegistry.ViewRegistry,
        constructors = (ViewRegistry.manage_addViewRegistryForm,
                        ViewRegistry.manage_addViewRegistry),
        icon = "www/silva_view_registry.gif"
        )

    context.registerClass(
        MultiViewRegistry.MultiViewRegistry,
        constructors = (MultiViewRegistry.manage_addMultiViewRegistryForm,
                        MultiViewRegistry.manage_addMultiViewRegistry),
        icon = "www/silva_multi_view_registry.gif"
        )
    
    context.registerClass(
        ExtensionService.ExtensionService,
        constructors = (ExtensionService.manage_addExtensionServiceForm,
                        ExtensionService.manage_addExtensionService),
        icon = "www/silva_view_registry.gif"
        )

    context.registerClass(
        File.FilesService,
        constructors = (File.manage_addFilesServiceForm, 
                        File.manage_addFilesService),
        icon = "www/files_service.gif"
        )

    # register xml import functions
    importer_registry.register_tag('silva_publication', Publication.xml_import_handler)
    importer_registry.register_tag('silva_folder', Folder.xml_import_handler)
    importer_registry.register_tag('silva_document', Document.xml_import_handler)
    importer_registry.register_tag('silva_demoobject', DemoObject.xml_import_handler)

    registerDirectory('views', globals())
    registerDirectory('widgets', globals())
    registerDirectory('globals', globals())
    registerDirectory('service_utils', globals())
