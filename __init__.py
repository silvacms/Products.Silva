# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.28 $
import Document, Folder, Root, ViewRegistry,\
       Publication, Ghost, Image, DemoObject

def initialize(context):
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
        ViewRegistry.ViewRegistry,
        constructors = (ViewRegistry.manage_addViewRegistryForm,
                        ViewRegistry.manage_addViewRegistry),
        icon = "www/silva_view_registry.gif"
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
        )

