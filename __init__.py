import Document, Folder, Root, ViewRegistry,\
       Publication, Ghost, ContactInfo, Image, Course

product_visibility = None # set to 'Global' to make visible in ZMI

def initialize(context):
     context.registerClass(
          Document.Document,
          constructors = (Document.manage_addDocumentForm,
                          Document.manage_addDocument),
          icon="www/silvadoc.gif",
	  visibility = product_visibility
          )
     
     context.registerClass(
          Folder.Folder,
          constructors = (Folder.manage_addFolderForm,
                          Folder.manage_addFolder),
          icon="www/silvafolder.gif",
	  visibility = product_visibility
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
	  icon="www/silvapublication.gif",
	  visibility = product_visibility
          )

     context.registerClass(
          Ghost.Ghost,
          constructors = (Ghost.manage_addGhostForm,
                          Ghost.manage_addGhost),
	  icon="www/silvaghost.gif",
	  visibility = product_visibility
          )

     context.registerClass(
          Course.Course,
          constructors = (Course.manage_addCourseForm,
                          Course.manage_addCourse),
	  icon="www/silvacourse.gif",
	  visibility = product_visibility
          )
     
     context.registerClass(
          ViewRegistry.ViewRegistry,
          constructors = (ViewRegistry.manage_addViewRegistryForm,
                          ViewRegistry.manage_addViewRegistry),
          icon="www/silva_view_registry.gif",
	  visibility = product_visibility
          )
     
     context.registerClass(
          ContactInfo.ContactInfo,
          constructors = (ContactInfo.manage_addContactInfoForm,
                          ContactInfo.manage_addContactInfo),
	  icon="www/silvacontactinfo.gif",
	  visibility = product_visibility
          )
     
     context.registerClass(
          Image.Image,
          constructors = (Image.manage_addImageForm,
                          Image.manage_addImage),
	  icon="www/silvaimage.gif",
	  visibility = product_visibility
          )

     context.registerClass(
          Ghost.GhostVersion,
          constructors = (Ghost.manage_addGhostVersionForm,
                          Ghost.manage_addGhostVersion),
	  visibility = product_visibility
          )

     context.registerClass(
          Course.CourseVersion,
          constructors = (Course.manage_addCourseVersionForm,
                          Course.manage_addCourseVersion),
	  visibility = product_visibility
          )
     
