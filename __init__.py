# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.73 $
import Metadata
import ViewRegistry, MultiViewRegistry
import Folder, Root
import Publication, Ghost, Image, File
import DemoObject, Indexer
import SQLDataSource
import install
import helpers # to execute the module_permission statements
from Products.Silva.ImporterRegistry import importer_registry
from ExtensionRegistry import extensionRegistry
import ExtensionService
import SimpleMembership
import EmailMessageService
import DocmaService
import Group
import VirtualGroup
import SidebarCache
import SidebarService
import UnicodeSplitter # To make the splitter register itself

# enable Formulator support for FileSystemSite
from Products.Formulator import FSForm
# so we can register directories for FileSystemSite
from Products.FileSystemSite.DirectoryView import registerDirectory, \
    registerFileExtension
from Products.FileSystemSite.FSImage import FSImage
# enable .ico support for FileSystemSite
registerFileExtension('ico', FSImage)

def initialize(context):
    extensionRegistry.register(
        'Silva', 'Silva Core', context, [
        Folder, Root, Publication, Ghost, Image, File,
        Indexer, SQLDataSource, DemoObject, Group, VirtualGroup],
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

    context.registerClass(
        SimpleMembership.SimpleMemberService,
        constructors = (SimpleMembership.manage_addSimpleMemberServiceForm,
                        SimpleMembership.manage_addSimpleMemberService),
        icon = "www/members.png"
        )

    context.registerClass(
        SimpleMembership.SimpleMember,
        constructors = (SimpleMembership.manage_addSimpleMemberForm,
                        SimpleMembership.manage_addSimpleMember),
        icon = "www/member.png"
        )

    context.registerClass(
        EmailMessageService.EmailMessageService,
        constructors = (EmailMessageService.manage_addEmailMessageServiceForm,
                        EmailMessageService.manage_addEmailMessageService),
        icon = "www/message_service.gif"
        )

    context.registerClass(
        DocmaService.DocmaService,
        constructors = (DocmaService.manage_addDocmaServiceForm,
                        DocmaService.manage_addDocmaService),
        icon = "www/docma.gif"
        )

    context.registerClass(
        SidebarService.SidebarService,
        constructors = (SidebarService.manage_addSidebarServiceForm, 
                        SidebarService.manage_addSidebarService),
        icon = ""
        )

    # register xml import functions
    # we let the xml import functionality of Publication handle any root elements, since a Silva instance can not import another root
    importer_registry.register_tag('silva_root', Publication.xml_import_handler)
    importer_registry.register_tag('silva_publication', Publication.xml_import_handler)
    importer_registry.register_tag('silva_folder', Folder.xml_import_handler)
    importer_registry.register_tag('silva_demoobject', DemoObject.xml_import_handler)

    # register the FileSystemSite directories
    registerDirectory('views', globals())
    registerDirectory('resources', globals())
    registerDirectory('globals', globals())
    registerDirectory('service_utils', globals())

    # initialize the metadata system
    #  register silva core types w/ metadata system
    #  register the metadata xml import initializers
    #  register a special accessor for ghosts
    Metadata.initialize_metadata()


