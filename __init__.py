# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.37 $
import Document, Folder, Root, ViewRegistry, MultiViewRegistry
import Publication, Ghost, Image, File
import DemoObject, CatalogedDemoObject
from Products.Silva.ImporterRegistry import importer_registry
# enable Formulator support for FileSystemSite
from Products.Formulator import FSForm
# so we can register directories for FileSystemSite
from Products.FileSystemSite.DirectoryView import registerDirectory, registerFileExtension
from Products.FileSystemSite.FSImage import FSImage
# enable .ico support for FileSystemSite
registerFileExtension('ico', FSImage)

def initialize(context):
    context.registerClass(
        File.FilesService,
        constructors = (
            File.manage_addFilesServiceForm, File.manage_addFilesService),
        icon = "www/files_service.gif"
        )

    context.registerClass(
        File.File,
        constructors = (
            File.manage_addFileForm, File.manage_addFile),
        icon="www/silvageneric.gif"
        )

    context.registerClass(
        Document.Document,
        constructors = (Document.manage_addDocumentForm,
                        Document.manage_addDocument),
        icon="www/silvadoc.gif"
        )
     
    context.registerClass(
        Folder.Folder,
        constructors = (Folder.manage_addFolderForm,
                        Folder.manage_addFolder),
        icon="www/silvafolder.gif"
        )  

    context.registerClass(
        Root.Root,
        constructors = (Root.manage_addRootForm,
                        Root.manage_addRoot)
        )

    context.registerClass(
        Publication.Publication,
        constructors = (Publication.manage_addPublicationForm,
                        Publication.manage_addPublication),
        icon="www/silvapublication.gif"
        )

    context.registerClass(
        Ghost.Ghost,
        constructors = (Ghost.manage_addGhostForm,
                        Ghost.manage_addGhost),
        icon="www/silvaghost.gif"
        )
           
    context.registerClass(
        Image.Image,
        constructors = (Image.manage_addImageForm,
                        Image.manage_addImage),
        icon="www/silvaimage.gif"
        )

    context.registerClass(
        Ghost.GhostVersion,
        constructors = (Ghost.manage_addGhostVersionForm,
                        Ghost.manage_addGhostVersion)
        )

    context.registerClass(
        DemoObject.DemoObject,
        constructors = (DemoObject.manage_addDemoObjectForm,
                        DemoObject.manage_addDemoObject),
        icon="www/silvageneric.gif"
        )       # generic icon for PluggableObjects

    context.registerClass(
        DemoObject.DemoObjectVersion,
        constructors = (DemoObject.manage_addDemoObjectVersionForm,
                        DemoObject.manage_addDemoObjectVersion),
        icon="www/silvageneric.gif"
        )


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
    
    #context.registerClass(
    #    CatalogedDemoObject.CatalogedDemoObject,
    #    constructors = (CatalogedDemoObject.manage_addCatalogedDemoObjectForm,
    #                    CatalogedDemoObject.manage_addCatalogedDemoObject)
    #    )

    #context.registerClass(
    #    CatalogedDemoObject.CatalogedDemoObjectVersion,
    #    constructors = (CatalogedDemoObject.manage_addCatalogedDemoObjectVersionForm,
    #                    CatalogedDemoObject.manage_addCatalogedDemoObjectVersion)
    #    )


    # register views & widgets
    #registerDirectory('views', globals())
    #registerDirectory('widgets', globals())

    # register xml import functions
    importer_registry.register_tag('silva_publication', Publication.xml_import_handler)
    importer_registry.register_tag('silva_folder', Folder.xml_import_handler)
    importer_registry.register_tag('silva_document', Document.xml_import_handler)
    importer_registry.register_tag('silva_demoobject', DemoObject.xml_import_handler)

    registerDirectory('views', globals())
    registerDirectory('widgets', globals())
    registerDirectory('globals', globals())
    registerDirectory('service_utils', globals())
