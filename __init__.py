import Document, Folder, Root, ViewRegistry,\
       Publication, Ghost, Image, DemoAddable

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
                        ViewRegistry.manage_addViewRegistry)
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
        DemoAddable.DemoAddable,
        constructors = (DemoAddable.manage_addDemoAddableForm,
                        DemoAddable.manage_addDemoAddable),
        icon="www/silvademo.gif"
        )

    context.registerClass(
        DemoAddable.DemoAddableVersion,
        constructors = (DemoAddable.manage_addDemoAddableVersionForm,
                        DemoAddable.manage_addDemoAddableVersion),
        icon="www/silvademo.gif"
        )

