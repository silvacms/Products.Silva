# Zope
import Acquisition
from Acquisition import aq_inner
from OFS import Folder, SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from OFS.CopySupport import _cb_decode # HACK
# Silva
from SilvaObject import SilvaObject
from Publishable import Publishable
import Copying
import Interfaces
import SilvaPermissions
import XMLImporter
# misc
import helpers
import re

class Folder(SilvaObject, Publishable, Folder.Folder):
    """Silva Folder.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Folder"

    __implements__ = Interfaces.Container
        
    def __init__(self, id, title):
        Folder.inheritedAttribute('__init__')(self, id, title)
        self._ordered_ids = []

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'move_object_up')
    def move_object_up(self, id):
        """Move object up. Returns true if move succeeded.
        """
        ids = self._ordered_ids
        try:
            i = ids.index(id)
        except ValueError:
            return 0
        if i == 0:
            return 0
        ids[i], ids[i - 1] = ids[i - 1], ids[i]
        self._ordered_ids = ids
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'move_object_down')
    def move_object_down(self, id):
        """move object down.
        """
        ids = self._ordered_ids
        try:
            i = ids.index(id)
        except ValueError:
            return 0
        if i == len(ids) - 1:
            return 0
        ids[i], ids[i + 1] = ids[i + 1], ids[i]
        self._ordered_ids = ids
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'move_to')
    def move_to(self, move_ids, index):
        ids = self._ordered_ids
        # check whether all move_ids are known
        for move_id in move_ids:
            if move_id not in ids:
                return 0
        ids_without_moving_ids = []
        move_ids_in_order = []
        for id in ids:
            if id in move_ids:
                move_ids_in_order.append(id)
                ids_without_moving_ids.append(None)
            else:
                ids_without_moving_ids.append(id)
        ids = ids_without_moving_ids
        move_ids = move_ids_in_order
        move_ids.reverse()
        for move_id in move_ids:
            ids.insert(index, move_id)
        ids = [id for id in ids if id is not None]
        self._ordered_ids = ids
        return 1

    def _refresh_ordered_ids(self, item):
        """Make sure item is in ordered_ids when it should be after
        active status changed.
        """
        if not Interfaces.Publishable.isImplementedBy(item):
            return
        if Interfaces.Content.isImplementedBy(item) and item.is_default():
            return
        ids = self._ordered_ids
        id = item.id
        if item.is_active() and id not in ids:
            ids.append(id)
            self._ordered_ids = ids
        if not item.is_active() and id in ids:
            ids.remove(id)
            self._ordered_ids = ids

    def _add_ordered_id(self, item):
        """Add item to the end of the list of ordered ids.
        """
        # this already happens to do what we want
        # this works in case of active objects that were added
        # (they're added to the list of ordered ids)
        # and also for inactive objects
        # (they're not added to the list; nothing happens)
        self._refresh_ordered_ids(item)
        
    def _remove_ordered_id(self, item):
        if not Interfaces.Publishable.isImplementedBy(item):
            return
        if Interfaces.Content.isImplementedBy(item) and item.is_default():
            return
        ids = self._ordered_ids
        if item.is_active() and item.id in ids:
            ids.remove(item.id)
            self._ordered_ids = ids
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent, 'refresh_active_publishables')
    def refresh_active_publishables(self):
        """Clean up all ordered ids in this container and all subcontainers.
        This method normally does not need to be called, but if something is
        wrong, this can be called in emergency situations. WARNING: all
        ordering information is lost!
        """
        ids = []
        for object in self.objectValues():
            if not Interfaces.Publishable.isImplementedBy(object):
                continue
            if Interfaces.Content.isImplementedBy(object) and object.is_default():
                continue
            if object.is_active():
                ids.append(object.id)
            if Interfaces.Container.isImplementedBy(object):
                object.refresh_active_publishables()
        self._ordered_ids = ids

    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'action_rename')
    def action_rename(self, orig_id, new_id):
        """Change id of object with id orig_id.
        """
        # check if new_id is valid
        if not self.is_id_valid(new_id):
            return
        # check if renaming (which in essence is the deletion of a url)
        # is allowed
        if not self.is_delete_allowed(orig_id):
            return
        # first change id if necessary
        if orig_id != new_id:
            self.manage_renameObject(orig_id, new_id)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'action_delete')
    def action_delete(self, ids):
        """Delete objects.
        """
        # check whether deletion is allowed
        deletable_ids = [id for id in ids if self.is_delete_allowed(id)]
        self.manage_delObjects(deletable_ids)
         
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'action_cut')      
    def action_cut(self, ids, REQUEST):
        """Cut objects.
        """
        # check whether deletion is allowed
        deletable_ids = [id for id in ids if self.is_delete_allowed(id)]
        # FIXME: need to do unit tests for this
        # FIXME: would this lead to a sensible user interface?
        self.manage_cutObjects(deletable_ids, REQUEST)
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'action_copy')
    def action_copy(self, ids, REQUEST):
        """Copy objects.
        """
        self.manage_copyObjects(ids, REQUEST)
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'action_paste')
    def action_paste(self, REQUEST):
        """Paste objects on clipboard.
        """
        # HACK
        # determine if we're cut-paste or copy-pasting, wish we
        # didn't have to..
        if not REQUEST.has_key('__cp'):
            return
        op, ref = _cb_decode(REQUEST['__cp'])

        # copy-paste operation
        # items on clipboard should be unapproved & closed, but
        # only the *copies*
        ids = []
        for item in self.cb_dataItems():
            #item.set_title(item.get_title())
            ids.append(item.id)
            
        if op == 0:
            # also update title of index documents
            copy_ids = ids
            # modify ids to copy_to if necessary
            paste_ids = []
            ids = self.objectIds()
            for copy_id in copy_ids:
                if copy_id in ids:
                    # FIXME: actually this does not reflect Zope's behavior,
                    # it has copy2_of, so we need to handle that..
                    paste_ids.append('copy_of_%s' % copy_id)
                else:
                    paste_ids.append(copy_id)
        else:
            # cut-paste operation
            cut_ids = ids
            # check where we're cutting from
            cut_container = item.aq_parent.get_container()
            # if not cutting to the same folder as we came from
            if self != cut_container:
                # modify ids to copy_to if necessary
                paste_ids = []
                ids = self.objectIds()
                for cut_id in cut_ids:
                    if cut_id in ids:
                        paste_ids.append('copy_of_%s' % cut_id)
                    else:
                        paste_ids.append(cut_id)
            else:
                # no changes to cut_ids 
                paste_ids = cut_ids
        # now we do the paste
        self.manage_pasteObjects(REQUEST=REQUEST)
        # now unapprove & close everything just pasted
        for paste_id in paste_ids:
            helpers.unapprove_close_helper(getattr(self, paste_id))
            
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'action_paste')
    def action_paste_to_ghost(self, REQUEST):
        """Paste what is on clipboard to ghost.
        """
        # create ghosts for each item on clipboard
        ids = self.objectIds()
        for item in self.cb_dataItems():
            paste_id = item.id
            while paste_id in ids:
                if Interfaces.VersionedContent.isImplementedBy(item):
                    paste_id = 'ghost_of_%s' % paste_id
                else:
                    paste_id = 'copy_of_%s' % paste_id
            self._ghost_paste(paste_id, item, REQUEST)

    def _ghost_paste(self, paste_id, item, REQUEST):
        if Interfaces.Container.isImplementedBy(item):
            # copy the container (but not its content)
            if item.meta_type == 'Silva Folder':
                self.manage_addProduct['Silva'].manage_addFolder(
                    paste_id, item.get_title(), 0)
            elif item.meta_type == 'Silva Publication':
                self.manage_addProduct['Silva'].manage_addPublication(
                    paste_id, item.get_title())
            else:
                raise NotImplementedError,\
                      "Unknown container ghost copy (%s)." % item.meta_type
            container = getattr(self, paste_id)
            for object in item.get_ordered_publishables():
                container._ghost_paste(object.id, object, REQUEST)
            # FIXME: ghost copy nonactives as well?
            for object in item.get_assets():
                container._ghost_paste(object.id, object, REQUEST)
        elif Interfaces.VersionedContent.isImplementedBy(item):
            if item.meta_type == 'Silva Ghost':
                # copy ghost
                version_id = item.get_public_version()
                if version_id is None:
                    version_id = item.get_next_version()
                if version_id is None:
                    version_id = item.get_last_closed_version()
                version = getattr(item, version_id)
                self.manage_addProduct['Silva'].manage_addGhost(
                    paste_id, version.get_content_url())
            else:
                # create ghost of item
                self.manage_addProduct['Silva'].manage_addGhost(
                    paste_id, item.absolute_url())
        else:
            # this is an object that just needs to be copied
            item = item._getCopy(self)
            item._setId(paste_id)
            self._setObject(paste_id, item)

    def action_import_xml(self, f):
        XMLImporter.importFile(self, f)
        
    # ACCESSORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_addables')
    def get_silva_addables(self):
        """Get a list of addable Silva objects.
        """
        result = []
        for meta_type in self.filtered_meta_types():
            if (meta_type.has_key('instance') and
                Interfaces.SilvaObject.isImplementedByInstancesOf(meta_type['instance'])):
                result.append(meta_type)
        return result
            
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_container')
    def get_container(self):
        """Get the container an object is in. Can be used with
        acquisition to get the 'nearest' container.
        FIXME: currently the container of a container is itself. Is this the right
        behavior? It leads to subtle bugs..
        """
        return self.aq_inner

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'container_url')
    def container_url(self):
        """Get url for container.
        """
        return self.absolute_url()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'is_transparent')
    def is_transparent(self):
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self):
        # NOTE: this is inefficient if there's a big unpublished hierarchy..
        # Folder is published if anything inside is published
        default = self.get_default()
        if default and default.is_published():
            return 1
        for object in self.get_ordered_publishables():        
            if object.is_published():
                return 1
        return 0

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'is_approved')
    def is_approved(self):
        # Folder is approved if anything inside is published
        default = self.get_default()
        if default and self.get_default().is_approved():
            return 1
        for object in self.get_ordered_publishables():        
            if object.is_approved():
                return 1
        return 0

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'is_delete_allowed')
    def is_delete_allowed(self, id):
        """Delete is only allowed if the object with id:
           - does not have an approved version
           - does not have a published version
           - if it is a container, does not contain anything of the
             above, recursively
        """
        object = getattr(self, id)
        if Interfaces.Publishable.isImplementedBy(object):
            return not object.is_published() and not object.is_approved()
        else:
            return 1

    _id_re = re.compile(r'^[a-zA-Z]\w*[a-zA-Z0-9]+$')

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'is_id_valid')
    def is_id_valid(self, id):
        """Check whether id is valid.
        """
        return self._id_re.search(id) is not None
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_default')
    def get_default(self):
        """Get the default content object of the folder.
        """
        if not hasattr(self.aq_base, 'index'):
            return None
        else:
            return getattr(self, 'index')
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_modification_datetime')
    def get_modification_datetime(self):
        """Folders don't really have a modification datetime.
        """
        return None
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_ordered_publishables')
    def get_ordered_publishables(self):
        return map(self._getOb, self._ordered_ids)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_nonactive_publishables')
    def get_nonactive_publishables(self):
        result = []
        for object in self.objectValues():
            if (Interfaces.Publishable.isImplementedBy(object) and
                not object.is_active()):
                result.append(object)
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_assets')
    def get_assets(self):
        result = []
        for object in self.objectValues():
            if Interfaces.Asset.isImplementedBy(object):
                result.append(object)
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_assets_of_type')
    def get_assets_of_type(self, meta_type):
        result = []
        for object in self.objectValues():
            if (Interfaces.Asset.isImplementedBy(object) and
                object.meta_type == meta_type):
                result.append(object)
        return result
    
    # FIXME: what if the objects returned are not accessible with my
    # permissions? unlikely as my role is acquired?
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_tree')
    def get_tree(self):
        """Get flattened tree of contents.
        """
        l = []
        self._get_tree_helper(l, 0)
        return l

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_container_tree')
    def get_container_tree(self):
        l = []
        self._get_container_tree_helper(l, 0)
        return l

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_tree')
    def get_public_tree(self):
        l = []
        self._get_public_tree_helper(l, 0)
        return l

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_status_tree')
    def get_status_tree(self):
        l = []
        self._get_status_tree_helper(l, 0)
        return l
    
    def _get_tree_helper(self, l, indent):
        for item in self.get_ordered_publishables():
            if (Interfaces.Container.isImplementedBy(item) and
                item.is_transparent()):
                l.append((indent, item))
                item._get_tree_helper(l, indent + 1)
            else:
                l.append((indent, item))

    def _get_container_tree_helper(self, l, indent):
        for item in self.get_ordered_publishables():
            if not Interfaces.Container.isImplementedBy(item):
                continue
            if item.is_transparent():
                l.append((indent, item))
                item._get_container_tree_helper(l, indent + 1)
            else:
                l.append((indent, item))

    def _get_public_tree_helper(self, l, indent):
        for item in self.get_ordered_publishables():
            if not item.is_published():
                continue
            if (Interfaces.Container.isImplementedBy(item) and
                item.is_transparent()):
                l.append((indent, item))
                item._get_public_tree_helper(l, indent + 1)
            else:
                l.append((indent, item))

    def _get_status_tree_helper(self, l, indent):
        for item in self.get_ordered_publishables():
            if Interfaces.Container.isImplementedBy(item):
                default = item.get_default()
                if default is not None:
                    l.append((indent, default))
                if item.is_transparent():
                    item._get_status_tree_helper(l, indent + 1)
            else:
                l.append((indent, item))
            
    def create_ref(self, obj):
        """Create a moniker for the object.
        """
        return Copying.create_ref(obj)

    def resolve_ref(self, ref):
        """Resolve reference to object.
        """
        return Copying.resolve_ref(self.getPhysicalRoot(), ref)

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, f):
        """Render object to XML.
        """
        f.write('<silva_folder id="%s">' % self.id)
        self._to_xml_helper(f)
        f.write('</silva_folder>')

    def _to_xml_helper(self, f):
        f.write('<title>%s</title>' % helpers.translateCdata(self.get_title()))
        default = self.get_default()
        if default is not None:
            default.to_xml(f)
        for object in self.get_ordered_publishables():
            if Interfaces.Publication.isImplementedBy(object):
                continue
            object.to_xml(f)
        #for object in self.get_assets():
        #    pass
            
InitializeClass(Folder)


manage_addFolderForm = PageTemplateFile("www/folderAdd", globals(),
                                        __name__='manage_addFolderForm')

def manage_addFolder(self, id, title, create_default=1, REQUEST=None):
    """Add a Folder."""
    if not self.is_id_valid(id):
        return
    object = Folder(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add doc
    if create_default:
        object.manage_addProduct['Silva'].manage_addDocument('index', '')
    helpers.add_and_edit(self, id, REQUEST)
    return ''



