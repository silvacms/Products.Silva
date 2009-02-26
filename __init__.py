# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Silva
import ContainerPolicy
# registers fields
from Products.Silva import emaillinesfield, lookupwindowfield
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.Silva.helpers import makeContainerFilter

try:
    # some people may have put Sprout in the Products directory
    # rather then somewhere in the PYTHONPATH, this makes Silva
    # import it
    import Products.Sprout
except ImportError:
    pass

#set havePIL here, so the Image add screen can determine
#allowed image filetypes, which are different depending
#on whether PIL is installed or not.  I don't like that
#havePIL is also defined in Image.py, and here it's used
#for the sole purpose of imported into untrusted pagetemplate
#land.
try:
    import PIL.Image
    havePIL = 1
except ImportError:
    havePIL = 0

#----------------------------------------
# Initialize subscription feature, part 1
#----------------------------------------
try:
    from Products.MaildropHost import MaildropHost
    MAILDROPHOST_AVAILABLE = True
except ImportError:
    MAILDROPHOST_AVAILABLE = False

MAILHOST_ID = 'service_subscriptions_mailhost'

def initialize(context):
    # import FileSystemSite functionality
    # (use CMFCore if FileSystemSite is not installed)
    from Products.Silva.fssite import registerDirectory, registerFileExtension
    from Products.Silva.fssite import FSImage
    from Products.Silva.fssite import FSDTMLMethod
    from Products.Silva.fssite import FSPageTemplate
    # enable .ico support for FileSystemSite
    registerFileExtension('ico', FSImage)

    from Products.Silva.silvaxml import xmlexport, xmlimport
    from Products.Silva.transform.renderer import defaultregistration

    import Folder, Root
    import Publication, Ghost, File, Link
    import GhostFolder
    import install
    import helpers # to execute the module_permission statements
    import mangle, batch
    from Products.Silva.ImporterRegistry import importer_registry
    from Products.Silva.ExtensionRegistry import extensionRegistry
    import ExtensionService
    import RendererRegistryService
    import SimpleMembership
    import EmailMessageService

    import TypographicalService

    import DocmaService
    import SidebarService
    import UnicodeSplitter # To make the splitter register itself
    import Metadata

    context.registerClass(
        Root.Root,
        constructors = (Root.manage_addRootForm,
                        Root.manage_addRoot),
        icon="www/silva.png",
        container_filter = makeContainerFilter(only_outside_silva=True)
        )
    registerTypeForMetadata(Root.Root.meta_type)

    context.registerClass(
        ExtensionService.ExtensionService,
        constructors = (ExtensionService.manage_addExtensionService,),
        icon = "www/extension_service.gif",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        RendererRegistryService.RendererRegistryService,
        constructors = (RendererRegistryService.manage_addRendererRegistryServiceForm,
                        RendererRegistryService.manage_addRendererRegistryService),
        icon = 'www/renderer_service.png',
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        File.FilesService,
        constructors = (File.manage_addFilesServiceForm,
                        File.manage_addFilesService),
        icon = "www/files_service.gif",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        SimpleMembership.SimpleMemberService,
        constructors = (SimpleMembership.manage_addSimpleMemberServiceForm,
                        SimpleMembership.manage_addSimpleMemberService),
        icon = "www/members.png",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        SimpleMembership.SimpleMember,
        constructors = (SimpleMembership.manage_addSimpleMemberForm,
                        SimpleMembership.manage_addSimpleMember),
        icon = "www/member.png",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        EmailMessageService.EmailMessageService,
        constructors = (EmailMessageService.manage_addEmailMessageServiceForm,
                        EmailMessageService.manage_addEmailMessageService),
        icon = "www/message_service.png",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        DocmaService.DocmaService,
        constructors = (DocmaService.manage_addDocmaServiceForm,
                        DocmaService.manage_addDocmaService),
        icon = "www/docma.png",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        SidebarService.SidebarService,
        constructors = (SidebarService.manage_addSidebarServiceForm,
                        SidebarService.manage_addSidebarService),
        icon = "www/sidebar_service.png",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        ContainerPolicy.ContainerPolicyRegistry,
        constructors = (ContainerPolicy.manage_addContainerPolicyRegistry, ),
        icon = "www/containerpolicy_service.png",
        container_filter = makeContainerFilter()
        )

    context.registerClass(
        TypographicalService.TypographicalService,
        constructors = (TypographicalService.manage_addTypographicalServiceForm,
                        TypographicalService.manage_addTypographicalService),
        icon = "www/typochars_service.png",
        container_filter = makeContainerFilter()
        )

    # register xml import functions (old style XML importer)
    # we let the xml import functionality of Publication handle any
    # root elements, since a Silva instance can not import another root
    importer_registry.register_tag('silva_root',
                                   Publication.xml_import_handler)
    importer_registry.register_tag('silva_publication',
                                   Publication.xml_import_handler)
    importer_registry.register_tag('silva_folder',
                                   Folder.xml_import_handler)
    importer_registry.register_tag('silva_ghostfolder',
                                   GhostFolder.xml_import_handler)
    importer_registry.register_tag('silva_link',
                                   Link.xml_import_handler)

    # register the FileSystemSite directories
    registerDirectory('views', globals())
    registerDirectory('resources', globals())
    registerDirectory('globals', globals())

    try:
        from Products import kupu
    except ImportError:
        pass
    else:
        registerDirectory('%s/common' % os.path.dirname(kupu.__file__),
                          globals())
        registerDirectory('%s/kupu' % os.path.dirname(__file__),
                          globals())

    # initialize the metadata system
    #  register silva core types w/ metadata system
    #  register the metadata xml import initializers
    #  register a special accessor for ghosts
    Metadata.initialize_metadata()
    initialize_icons()
    initialize_upgrade()

    #------------------------------
    # Initialize the XML registries
    #------------------------------

    xmlexport.initializeXMLExportRegistry()
    xmlimport.initializeXMLImportRegistry()

    #-------------------------------------
    # Initialize the Renderer Registration
    #-------------------------------------

    defaultregistration.registerDefaultRenderers()

    #----------------------------------------
    # Initialize subscription feature, part 2
    #----------------------------------------
    from Products.Silva import subscriptionservice

    #extensionRegistry.register(
    #    'SilvaSubscriptions', 'Silva Subscriptions', context, [],
    #    install, depends_on='Silva')

    context.registerClass(
        subscriptionservice.SubscriptionService,
        constructors = (
            subscriptionservice.manage_addSubscriptionServiceForm,
            subscriptionservice.manage_addSubscriptionService),
        icon = "www/subscription_service.png",
        container_filter = makeContainerFilter()
        )

    #if MAILDROPHOST_AVAILABLE:
    #    zLOG.LOG('Silva Subscriptions', zLOG.INFO, (
    #        'The MaildropHost is available and could be used for mail delivery. '
    #        'If the MaildropHost is indeed in use, please be sure to start '
    #        'the seperate mail delivery process.'))

#------------------------------------------------------------------------------
# External Editor support
#------------------------------------------------------------------------------

# check if ExternalEditor is available
import os
from Globals import DTMLFile

try:
    #   import Product.ExternalEditor as ee
    import Product.ExternalEditor as ee
except ImportError:
    pass
else:
    dirpath = os.path.dirname(ee.__file__)
    dtmlpath = '%s/manage_main' % dirpath
    Folder.manage_main = DTMLFile(dtmlpath, globals())


def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('mangle', 'batch', 'adapters',
                        'version_management', 'path')

from AccessControl import allow_module

allow_module('Products.Silva.adapters.security')
allow_module('Products.Silva.adapters.cleanup')
allow_module('Products.Silva.adapters.renderable')
allow_module('Products.Silva.adapters.version_management')
allow_module('Products.Silva.adapters.archivefileimport')
allow_module('Products.Silva.adapters.languageprovider')
allow_module('Products.Silva.adapters.zipfileimport')
allow_module('Products.Silva.adapters.path')
allow_module('Products.Silva.roleinfo')
allow_module('Products.Silva.i18n')
allow_module('Products.Silva.mail')

def initialize_icons():
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

def initialize_upgrade():
    # initialize all upgrades so they're available for doing partial upgrades
    from Products.Silva import upgrade_092
    upgrade_092.initialize()

    from Products.Silva import upgrade_093
    upgrade_093.initialize()

    from Products.Silva import upgrade_100
    upgrade_100.initialize()

    from Products.Silva import upgrade_110
    upgrade_110.initialize()

    from Products.Silva import upgrade_120
    upgrade_120.initialize()

    from Products.Silva import upgrade_130
    upgrade_130.initialize()

    from Products.Silva import upgrade_140
    upgrade_140.initialize()

    from Products.Silva import upgrade_150
    upgrade_150.initialize()

    from Products.Silva import upgrade_160
    upgrade_160.initialize()

    from Products.Silva import upgrade_200
    upgrade_200.initialize()

    from Products.Silva import upgrade_210
    upgrade_210.initialize()

#------------------------------------------------------------------------------
# Monkey patches
#------------------------------------------------------------------------------

import monkey
monkey.patch_all()
