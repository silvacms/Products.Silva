# Zope
import Acquisition
from Acquisition import aq_inner
from OFS import Folder, SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
# Silva
from ViewRegistry import ViewAttribute
from SilvaObject import SilvaObject
from Publishable import Publishable
import Copying
import Interfaces
# misc
from helpers import add_and_edit

class Folder(Publishable, Folder.Folder):
    """Silva Folder.
    """
    meta_type = "Silva Folder"

    __implements__ = Interfaces.Container
    
    security = ClassSecurityInfo()

    # allow edit view on this object
    edit = ViewAttribute('edit')
    
    def __init__(self, id, title):
        self.id = id
        self._title = title
        self._ordered_ids = []

    # MANIPULATORS
    def set_title(self, title):
        """Set the title of this folder.
        """
        self._title = title 

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
        """Make sure item is in ordered_ids when it should be.
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
              
    # ACCESSORS

    def get_folder(self):
        """Get the folder an object is in. Can be used with
        acquisition to get the 'nearest' folder.
        """
        return self.aq_inner
    
    def folder_url(self):
        """Get url for folder.
        """
        return self.absolute_url()

    def title(self):
        """Get the title.
        """
        return self._title
    
    def is_published(self):
        """Return true if this is published."""
        #for item in self.objectValues(['Silva Folder', 'Silva Document']):
        #    if item.is_published():
        #        return 1            
        return 1
            
    def is_transparent(self):
        return 1

    def get_default(self):
        """Get the default content object of the folder.
        """
        # NOTE: another dependency on hardcoded name 'default'
        return getattr(self, 'default', None)
    
    def get_ordered_publishables(self):
        return map(self._getOb, self._ordered_ids)
    
    def get_nonactive_publishables(self):
        result = []
        for object in self.objectValues():
            if (Interfaces.Publishable.isImplementedBy(object) and
                not object.is_active()):
                result.append(object)
        return result
    
    def get_assets(self):
        result = []
        for object in self.objectValues():
            if Interfaces.Asset.implementedBy(object):
                result.append(object)
        return result
    
    def get_tree(self):
        """Get flattened tree of contents.
        """
        l = []
        self._get_tree_helper(l, 0)
        return l

    def get_container_tree(self):
        l = []
        self._get_container_tree_helper(l, 0)
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
                
    def create_ref(self, obj):
        """Create a moniker for the object.
        """
        return Copying.create_ref(obj)

    def resolve_ref(self, ref):
        """Resolve reference to object.
        """
        return Copying.resolve_ref(self.getPhysicalRoot(), ref)
    
    def action_rename(self, ref, id, title):
        """Rename object moniker refers to.
        """
        object = Copying.resolve_ref(self.getPhysicalRoot(), ref)
        # first change id if necessary
        if object.id != id:
            parent = object.aq_inner.aq_parent
            parent.manage_renameObject(object.id, id)
        # now change title
        object.set_title(title)
    
    def action_delete(self, refs):
        """Delete objects monikers refer to.
        """
        Copying.delete(self.getPhysicalRoot(), refs)

    def action_cut(self, refs, REQUEST):
        """Cut objects.
        """
        Copying.cut(self.getPhysicalRoot(), refs, REQUEST)
        
    def action_copy(self, refs, REQUEST):
        """Copy objects.
        """
        Copying.copy(self.getPhysicalRoot(), refs, REQUEST)

    def action_paste(self, REQUEST):
        """Paste objects on clipboard.
        """
        if self.can_paste(REQUEST):
            Copying.paste(self, REQUEST=REQUEST)
    
    def action_paste_to(self, ref, REQUEST):
        """Paste objects on clipboard to ref.
        """
        obj = Copying.resolve_ref(self.getPhysicalRoot(), ref)
        obj.action_paste(REQUEST)

    def action_dedent(self, ref):
        """Dedent object.
        """
        # get object to dedent
        root = self.getPhysicalRoot()
        object = Copying.resolve_ref(root, ref)
        # folder we're dedenting from
        from_folder = object.aq_parent
        # folder we're dedenting to
        to_folder = from_folder.aq_parent
        # can't move to something that is not a normal folder
        if not Interfaces.Container.isImplementedBy(to_folder):
            return None
        # can't dedent anything not in _toc_ids
        toc_ids = from_folder._toc_ids
        if object.id not in toc_ids:
            return None
        # can't dedent 'default'
        if object.id == 'default':
            return None
        # now cut & paste object
        cb = Copying.cut(root, [ref])
        Copying.paste(to_folder, cb_copy_data=cb)
        # find position of from_folder in to_folder
        toc_ids = to_folder._toc_ids
        i = toc_ids.index(from_folder.id)
        # add object to toc_ids of to_folder,
        # just after position of from_folder
        toc_ids.remove(object.id)
        toc_ids.insert(i + 1, object.id)
        to_folder._toc_ids = toc_ids
        return 1
    
    def can_paste(self, REQUEST):
        """Can we paste what is in clipboard to this object?"""
        return 1
        
Globals.InitializeClass(Folder)

manage_addFolderForm = PageTemplateFile("www/folderAdd", globals(),
                                        __name__='manage_addFolderForm')

def manage_addFolder(self, id, title, create_default=1, REQUEST=None):
    """Add a Folder."""
    object = Folder(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add doc
    if create_default:
        object.manage_addProduct['Silva'].manage_addDocument('default', '')
    add_and_edit(self, id, REQUEST)
    return ''



