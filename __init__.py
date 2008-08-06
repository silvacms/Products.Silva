# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

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


# register this extension
from silva.core import conf
conf.extensionName('Silva')
conf.extensionTitle('Silva Core')
conf.extensionDepends(None)

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
    from Products.Silva.silvaxml import xmlexport, xmlimport
    # import FileSystemSite functionality
    # (use CMFCore if FileSystemSite is not installed)
    from Products.Silva.fssite import registerDirectory, registerFileExtension
    from Products.Silva.fssite import FSImage
    from Products.Silva.fssite import FSDTMLMethod
    from Products.Silva.fssite import FSPageTemplate
    # enable .ico support for FileSystemSite
    registerFileExtension('ico', FSImage)
    
    from Products.Silva.silvaxml import xmlexport
    
    import Root
    import install
    import helpers # to execute the module_permission statements
    import mangle, batch
    from Products.Silva.ImporterRegistry import importer_registry
    from Products.Silva.ExtensionRegistry import extensionRegistry

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

    #------------------------------
    # Initialize the XML registries
    #------------------------------
    
    xmlexport.initializeXMLExportRegistry()
    

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

allow_module('Products.Silva.adapters.views')
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


#------------------------------------------------------------------------------
# Monkey patches
#------------------------------------------------------------------------------

import monkey
monkey.patch_all()
