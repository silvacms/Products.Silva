# Copyr2ght (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.97 $

import Metadata
import Folder, Root
import Publication, Ghost, Image, File, SimpleContent
import DemoObject, Indexer
import SQLDataSource
import GhostFolder
import SemiGhost
import AutoTOC
import install
import helpers # to execute the module_permission statements
import mangle, batch
from Products.Silva.ImporterRegistry import importer_registry
from Products.Silva.ExtensionRegistry import extensionRegistry
import ExtensionService
import SimpleMembership
import EmailMessageService
import DocmaService
import Group
import VirtualGroup
import IPGroup
import SidebarCache
import SidebarService
import UnicodeSplitter # To make the splitter register itself
import ContainerPolicy

from Products.Silva import icon

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
        Indexer, SQLDataSource, DemoObject, Group, VirtualGroup, IPGroup,
        GhostFolder, SemiGhost, AutoTOC],
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
        icon = "www/message_service.png"
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
        icon = "www/service_sidebar.gif"
        )
    context.registerClass(
        ContainerPolicy.ContainerPolicyRegistry,
        constructors = (ContainerPolicy.manage_addContainerPolicyRegistry, ),
        icon = "www/service.png"
        )
        
    # register xml import functions
    # we let the xml import functionality of Publication handle any root elements, since a Silva instance can not import another root
    importer_registry.register_tag('silva_root', Publication.xml_import_handler)
    importer_registry.register_tag('silva_publication', Publication.xml_import_handler)
    importer_registry.register_tag('silva_folder', Folder.xml_import_handler)
    importer_registry.register_tag('silva_demoobject', DemoObject.xml_import_handler)
    importer_registry.register_tag('silva_ghostfolder',
        GhostFolder.xml_import_handler)

    # register the FileSystemSite directories
    registerDirectory('views', globals())
    registerDirectory('resources', globals())
    registerDirectory('globals', globals())

    # initialize the metadata system
    #  register silva core types w/ metadata system
    #  register the metadata xml import initializers
    #  register a special accessor for ghosts
    Metadata.initialize_metadata()
    initialize_icons()

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


def __allow_access_to_unprotected_subobjects__(name, value=None):
    if name in ('mangle', 'batch', ):
        return 1
    return 0


def initialize_icons():
    icon.registry.registerAdapter(icon.MetaTypeClassAdapter, 0)
    icon.registry.registerAdapter(icon.MetaTypeAdapter, 5)
    icon.registry.registerAdapter(icon.SilvaFileAdapter, 10)
    icon.registry.registerAdapter(GhostFolder.GhostFolderIconAdapter, 11)
    icon.registry.registerAdapter(Ghost.GhostIconAdapter, 12)
    mimeicons = [
        ('audio/aiff', 'file_aiff.png'),
        ('audio/x-aiff', 'file_aiff.png'),
        ('audio/basic', 'file_aiff.png'),
        ('audio/x-gsm', 'file_aiff.png'),
        ('audio/mid', 'file_aiff.png'),
        ('audio/midi', 'file_aiff.png'),
        ('audio/x-midi', 'file_aiff.png'),
        ('audio/mpeg', 'file_aiff.png'),
        ('audio/x-mpeg', 'file_aiff.png'),
        ('audio/mpeg3', 'file_aiff.png'),
        ('audio/x-mpeg3', 'file_aiff.png'),
        ('audio/mp3', 'file_aiff.png'),
        ('audio/x-mp3', 'file_aiff.png'),
        ('audio/x-m4a', 'file_aiff.png'),
        ('audio/x-m4p', 'file_aiff.png'),
        ('audio/mp4', 'file_aiff.png'),
        ('audio/wav', 'file_aiff.png'),
        ('audio/x-wav', 'file_aiff.png'),
        ('application/msword', 'file_doc.png'),
        ('application/postscript', 'file_illustrator.png'),
        ('application/x-javascript', 'file_js.png'),
        ('application/pdf', 'file_pdf.png'),
        ('application/vnd.ms-powerpoint', 'file_ppt.png'),
        ('application/x-rtsp', 'file_quicktime.png'),
        ('application/sdp', 'file_quicktime.png'),
        ('application/x-sdp', 'file_quicktime.png'),
        ('application/vnd.ms-excel', 'file_xls.png'),
        ('application/x-zip-compressed', 'file_zip.png'),
        ('text/plain', 'file_txt.png'),
        ('text/css', 'file_css.png'),
        ('text/html', 'file_html.png'),
        ('text/xml', 'file_xml.png'),
        ('video/avi', 'file_quicktime.png'),
        ('video/msvideo', 'file_quicktime.png'),
        ('video/x-msvideo', 'file_quicktime.png'),
        ('video/mp4', 'file_quicktime.png'),
        ('video/mpeg', 'file_quicktime.png'),
        ('video/x-mpeg', 'file_quicktime.png'),
        ('video/quicktime', 'file_quicktime.png'),
        ('video/x-dv', 'file_quicktime.png'),
    ]
    ri = icon.registry.registerIcon
    for mimetype, icon_name in mimeicons:
        ri(('mime_type', mimetype), 'www/%s' % icon_name, File.__dict__)

    misc_icons = [
        ('ghostfolder', 'folder', 'silvaghostfolder.gif'),
        ('ghostfolder', 'publication', 'silvaghostpublication.gif'),
        ('ghostfolder', 'link_broken', 'silvaghostbroken.png'),
        ('ghost', 'link_ok', 'silvaghost.gif'),
        ('ghost', 'link_broken', 'silvaghostbroken.png'),
    ]
    for klass, kind, icon_name in misc_icons:
        ri((klass, kind), 'www/%s' % icon_name, GhostFolder.__dict__)


