from ISilvaObject import ISilvaObject

def from085to086(self, root):
    """Upgrade Silva from 0.8.5 to 0.8.6 as a simple matter of programming.
    """
    # rename silva root so we can drop in fresh new one
    id = root.id
    backup_id = id + '_085'
    self.manage_renameObject(id, backup_id)
    orig_root = getattr(self, backup_id)
    # create new silva root
    self.manage_addProduct['Silva'].manage_addRoot(id, orig_root.title)
    dest_root = getattr(self, id)
    # wipe out layout stuff from root as we're going to copy it over
    delete_ids = [obj.getId() for obj in dest_root.objectValues() if
                  obj.meta_type in ['DTML Method', 'Script (Python)', 'Page Template']]
    dest_root.manage_delObjects(delete_ids)

    # now copy over silva contents from old root; everything should be a
    # SilvaObject
    copy_ids = [obj.getId() for obj in orig_root.objectValues() if
                ISilvaObject.isImplementedBy(obj)]
    cb = orig_root.manage_copyObjects(copy_ids)
    dest_root.manage_pasteObjects(cb_copy_data=cb)

    # also copy over layout stuff
    layout_ids = [obj.getId() for obj in orig_root.objectValues() if
                  obj.meta_type in ['DTML Method', 'Script (Python)', 'Page Template']]
    
    cb = orig_root.manage_copyObjects(layout_ids)
    dest_root.manage_pasteObjects(cb_copy_data=cb)

    # now to copy over properties

    # figure out what changed
    dest_properties = dest_root.propertyIds()
    new_properties = []
    changed_properties = []
    for id in orig_root.propertyIds():
        if id in dest_properties:
            changed_properties.append(id)
        else:
            new_properties.append(id)
    # alter properties that need to be altered
    for id in changed_properties:
        dest_root.manage_changeProperties({id: orig_root.getProperty(id)})
    # add properties that need to be added
    for id in new_properties:
        dest_root.manage_addProperty(id, orig_root.getProperty(id),
                                     orig_root.getPropertyType(id))
    
    # now copy over the roles information
    if hasattr(orig_root, '__ac_local_roles__'):
        dest_root.__ac_local_roles__ = orig_root.__ac_local_roles__
    if hasattr(orig_root, '__ac_local_groups__'):
        dest_root.__ac_local_groups__ = orig_root.__ac_local_groups__

    # if there's an 'acl_users', 'images', or 'locals' copy that over as well.
    to_copy_ids = []
    for id in ['acl_users', 'images', 'locals']:
        if hasattr(orig_root.aq_base, id):
            to_copy_ids.append(id)
    cb = orig_root.manage_copyObjects(to_copy_ids)
    dest_root.manage_pasteObjects(cb_copy_data=cb)

    # copy over order information
    dest_root._ordered_ids = orig_root._ordered_ids
    
    # we still may not have everything, but a good part..
    # should advise the upgrader to copy over the rest by hand
    
