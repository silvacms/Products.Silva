import Document, Folder, Root, ViewRegistry, Publication, Ghost

def initialize(context):
     context.registerClass(
          Document.Document,
          constructors = (Document.manage_addDocumentForm,
                          Document.manage_addDocument),
          icon="www/silva_document.gif"
          )
     
     context.registerClass(
          Folder.Folder,
          constructors = (Folder.manage_addFolderForm,
                          Folder.manage_addFolder),
          icon="www/silva_folder.gif" 
          )  

     context.registerClass(
          Root.Root,
          constructors = (Root.manage_addRootForm,
                          Root.manage_addRoot)
          )

     context.registerClass(
          Publication.Publication,
          constructors = (Publication.manage_addPublicationForm,
                          Publication.manage_addPublication)
          )

     context.registerClass(
          Ghost.Ghost,
          constructors = (Ghost.manage_addGhostForm,
                          Ghost.manage_addGhost)
          )
     
     context.registerClass(
          ViewRegistry.ViewRegistry,
          constructors = (ViewRegistry.manage_addViewRegistryForm,
                          ViewRegistry.manage_addViewRegistry),
          icon="www/silva_view_registry.gif"
          )
     
