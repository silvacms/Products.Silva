# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.4 $
from ISecurity import ISecurity

class ISilvaObject(ISecurity):
    """Interface that should be supported by all Silva objects.
    """
    # MANIPULATORS
    def set_title(title):
        """Change the title of the content object.
        """
        pass

    # MANIPULATORS
    def manage_afterAdd(item, container):
        """Hook called by Zope just after the item was added to
        container. Adds item id to an ordered list, if item is
        a publishable object.
        """
        pass

    def manage_beforeDelete(item, container):
        """Hook called by Zope just before the item is deleted from
        container. Removes item id to from ordered list (item is
        a publishable object).
        """
        pass        

    # ACCESSORS
    def get_title():
        """The title of the content object.
        PUBLIC
        """
        pass

    def get_title_or_id():
        """The title or id of the content object.
        PUBLIC
        """
        pass

    def get_creation_datetime():
        """Creation datetime of the object. Return None if not supported.
        PUBLIC
        """
        pass

    def get_modification_datetime():
        """Last modification datetime of the object. Return None if not
        supported.
        PUBLIC
        """
        pass

    def get_breadcrumbs():
        """Get the objects above this item, until the Silva Root, in
        order from Silva Root.
        PUBLIC
        """
        pass
        
    def get_editable():
        """Get the editable version (may be object itself if no versioning).
        Returns None if there is no such version.
        """
        pass

    def get_previewable():
        """Get the previewable version (may be the object itself if no
        versioning).
        Returns None if there is no such version.
        """
        pass
   
    def get_viewable():
        """Get the publically viewable version (may be the object itself if
        no versioning).
        Returns None if there is no such version.
        """
        pass

    def preview():
        """Render this object using the public view defined in the view registry.
        This should use methods on the object itself and the version object
        obtained by get_previewable() to render the object to HTML.
        """
        pass
    
    def view():
        """Render this object using the public view defined in the view registry.
        This should use methods on the object itself and the version object
        obtained by get_viewable() to render the object to HTML.
        PUBLIC
        """
        pass

    def get_xml():
        """Render this object as XML, return as string in UTF-8 encoding.
        """
        pass
    
    def to_xml(f):
        """Render this object as XML, write unicode to fileobject f.
        """
        pass

    def implements_publishable():
        """This object implements IPublishable."""

    def implements_asset():
        """This object implements IAsset."""

    def implements_content():
        """This object implements IContent."""

    def implements_container():
        """This object implements IContainer."""

    def implements_publication():
        """This object implements IPublication."""

    def implements_versioned_content():
        """This object implements IVersionedContent."""

    
