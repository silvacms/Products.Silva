from ISilvaObject import ISilvaObject
from IPublishable import IPublishable

class IContainer(ISilvaObject, IPublishable):
    
    # MANIPULATORS
    def move_object_up(id):
        """Move object with id up in the list of ordered publishables.
        Return true in case of success.
        """
        pass

    def move_object_down(id):
        """Move object with id down in the list of ordered publishables.
        Return true in case of success.
        """
        pass

    def move_to(move_ids, index):
        """Move ids just before index.
        Return true in case success.
        """
        pass

    def action_rename(orig_id, new_id):
        """Rename subobject with orig_id into new_id.
        Cannot rename approved or published content.
        """
        pass
    
    def action_delete(ids):
        """Delete ids in this container.
        Cannot delete approved or published content.
        """
        pass

    def action_cut(ids, REQUEST):
        """Cut ids in this folder, putting them on clipboard in REQUEST.
        Cannot cut approved or published content.
        """
        pass

    def action_copy(ids, REQUEST):
        """Copy ids in this folder, putting them on clipboard in REQUEST.
        """
        pass

    def action_paste(REQUEST):
        """Paste clipboard to this folder.
        After paste, approved or published content is automatically
        unapproved and/or closed.
        """
        pass
        
    # ACCESSORS
    def get_silva_addables():
        """Get a list of meta_type_dicts (from filtered_meta_types()) that
        are addable to this container.
        """
        pass

    def get_silva_addables_all():
        """Get a list of meta_types of all addables that exist in
        Silva.
        """
        
    def get_silva_addables_allowed():
        """Gives a list of all meta_types that are explicitly allowed here.
        """
        
    def get_container():
        """Get the nearest container in the acquisition hierarchy.
        (this one)
        """
        pass

    def container_url():
        """Get the url of the nearest container.
        """
        pass
    
    def is_transparent():
        """Show this subtree in get_tree().
        """
        pass

    def is_delete_allowed(id):
        """Return true if subobject with name 'id' can be deleted.
        This is only allowed if the subobject is not published or
        approved.
        """
        pass
    
    def get_default():
        """Get the default content object of the folder. If
        no default is available, return None.
        """
        pass

    def get_ordered_publishables():
        """Get list of active publishables of this folder, in
        order.
        """
        pass
    
    def get_nonactive_publishables():
        """Get a list of nonactive publishables. This is not in
        any fixed order.
        """
        pass
    
    def get_assets():
        """Get a list of non-publishable objects in this folder.
        (not in any order).
        """
        pass

    def get_assets_of_type():
        """Get list of assets of a certain meta_type.
        """
        pass
    
    def get_tree():
        """Get flattened tree of all active publishables.
        This is a list of indent, object tuples.
        """
        pass

    def get_container_tree():
        """Get flattened tree of all sub-containers.
        This is a list of indent, object tuples.
        """
        pass

    def get_public_tree():
        """Get tree of all publishables that are public.
        """
        pass

    def get_status_tree():
        """Get tree of all active content objects. For containers,
        show the default object if available.
        """
        pass
