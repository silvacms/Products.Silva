# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.79 $
import Metadata
import Folder, Root
import Publication, Ghost, Image, File, SimpleContent
import DemoObject, Indexer
import SQLDataSource
import GhostFolder
import install
import helpers # to execute the module_permission statements
import mangle
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
import ContainerPolicy

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
        Folder, Root, Publication, Ghost, Image, File, SimpleContent,
        Indexer, SQLDataSource, DemoObject, Group, VirtualGroup,
        GhostFolder],
        install, depends_on=None)

    context.registerClass(
        ExtensionService.ExtensionService,
        constructors = (ExtensionService.manage_addExtensionServiceForm,
                        ExtensionService.manage_addExtensionService),
        icon = "www/extension_service.gif"
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
    context.registerClass(
        ContainerPolicy.ContainerPolicyRegistry,
        constructors = (ContainerPolicy.manage_addContainerPolicyRegistry, ),
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

#------------------------------------------------------------------------------
# External Editor support
#------------------------------------------------------------------------------

# check if ExternalEditor is available
import os
from Globals import DTMLFile

try:
    import Product.ExternalEditor as ee
except ImportError:
    pass
else:
    dirpath = os.path.dirname(ee.__file__)
    dtmlpath = '%s/manage_main' % dirpath
    Folder.manage_main = DTMLFile(dtmlpath, globals())


