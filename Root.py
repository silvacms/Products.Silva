# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.70 $

# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass, DTMLFile
from DateTime import DateTime
# Silva
from Publication import Publication
import SilvaPermissions
import install
# misc
from helpers import add_and_edit

from Products.Silva.Metadata import export_metadata

from interfaces import IRoot, IVersionedContent, IContainer

icon="globals/silva.gif"

class Root(Publication):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Root"

    __implements__ = IRoot

    inherited_manage_options = Publication.manage_options
    manage_options= (
        (inherited_manage_options[0],) + # ({'label':'Contents', 'action':'manage_contents'},) +
        ({'label':'Services', 'action':'manage_services'},) +
        inherited_manage_options[1:]
        )

    def __init__(self, id):
        Root.inheritedAttribute('__init__')(self, id)
        # if we add a new root, version starts out as the software version
        self._content_version = self.get_silva_software_version()
    
    # MANIPULATORS

    def manage_afterAdd(self, item, container):
        # since we're root, we don't want to notify our container
        # we do, however, have to add ourselves to the catalog then
        self.index_object()
        
    def manage_beforeDelete(self, item, container):
        # since we're root, we don't want to notify our container
        # we do, however, have to remove ourselves from the catalog
        self.unindex_object()

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_main')
    manage_main = DTMLFile(
        'www/folderContents', globals())
    
    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_services')
    manage_services = DTMLFile(
        'www/folderServices', globals())

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Don't do anything here. Can't do this with root.
        """
        pass

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'add_silva_addable_forbidden')
    def add_silva_addable_forbidden(self, meta_type):
        """Add a meta_type that is forbidden from use in this site.
        """
        addables_forbidden = getattr(self.aq_base, '_addables_forbidden', {})
        addables_forbidden[meta_type] = 0
        self._addables_forbidden = addables_forbidden

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'clear_silva_addables_forbidden')
    def clear_silva_addables_forbidden(self):
        """Clear out all forbidden addables; everything allowed now.
        """
        self._addables_forbidden = {}
        
    # ACCESSORS
    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'serviceIds')
    def serviceIds(self):
        """Show all service ids.
        """
        return [id for id in Root.inheritedAttribute('objectIds')(self)
                if id.startswith('service_')]
        
    security.declarePublic('objectItemsContents')
    def objectItemsContents(self, spec=None):
        """Don't display services by default in the Silva root.
        """
        return [item for item in Root.inheritedAttribute('objectItems')(self)
                if not item[0].startswith('service_')]

    security.declarePublic('objectItemsServices')
    def objectItemsServices(self, spec=None):
        """Display services separately.
        """
        return [item for item in Root.inheritedAttribute('objectItems')(self)
                if item[0].startswith('service_')]
 
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_root')
    def get_root(self):
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        return self.aq_inner

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_root_url')
    def get_root_url(self):
        """Get url of root of site.
        """
        return self.aq_inner.absolute_url()

    # FIXME: Being deprecated, will be deleted in the near future
    silva_root = get_root_url
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
        f = context.f
        f.write('<silva_root id="%s">' % self.id)
        
        self._to_xml_helper(context)
        export_metadata(self, context)
        
        f.write('</silva_root>')

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_addables_allowed_in_publication')
    def get_silva_addables_allowed_in_publication(self):
        # allow everything in silva by default, unless things are restricted
        # explicitly
        addables = self._addables_allowed_in_publication
        if addables is None:
            return self.get_silva_addables_all()
        else:
            return addables

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_silva_addable_forbidden')
    def is_silva_addable_forbidden(self, meta_type):
        """Return true if addable is forbidden to be used in this
        site.
        """
        if not hasattr(self.aq_base, '_addables_forbidden'):
            return 0
        else:
            return self._addables_forbidden.has_key(meta_type)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_software_version')
    def get_silva_software_version(self):
        """The version of the Silva software.
        """
        return '0.9.2'
    
    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_content_version')
    def get_silva_content_version(self):
        """Return the version of Silva content.

        This version is usually the same as the software version, but
        can be different in case the content was not yet updated.
        """
        return getattr(self, '_content_version', 'before 0.9.2')
    
    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'upgrade_silva')
    def upgrade_silva(self, from_version='0.9.1'):
        """Upgrade Silva from previous version.
        """
        if not from_version == '0.9.1':
            raise "Not supported", "Upgrading from another version than 0.9.1 is not supported."
        import upgrade
        my_id = self.id
        ret = upgrade.from091to092(self.aq_inner.aq_parent, self)
        self._content_version = self.get_silva_software_version()
        return ret or "Upgrade of %s succeeded." \
               % my_id

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'status_update')
    def status_update(self):
        """Updates status for objects that need status updated

        Searches the ZCatalog for objects that should be published or closed
        and updates the status accordingly
        """
        if not getattr(self, 'service_catalog', None):
            return 'No catalog found!'
        
        # first get all approved objects that should be published
        query = {'silva-extrapublicationtime': DateTime(),
                 'silva-extrapublicationtime_usage': 'range:max',
                 'version_status': 'approved'
                }

        result = self.service_catalog(query)

        # now get all published objects that should be closed
        query = {'silva-extraexpirationtime': DateTime(),
                 'silva-extraexpirationtime_usage': 'range:max',
                 'version_status': 'public'
                }

        result += self.service_catalog(query)
        
        for item in result:
            ob = item.getObject()
            ob.object()._update_publication_status()

        return 'Status updated'

    security.declarePublic('rollbackTransaction')
    def recordError(self, message_type, message):
        """record given error/feedback
        
            actual logging is not implemented, just an idea; what really 
            happens is a ZODB transaction rollback if message_type == 'error'

            message_type: either 'feedback' or 'error'
            message: string containing user readable error
            returns None
        """
        if message_type == 'error':
            get_transaction().abort()

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'delete_old_versions')
    def delete_old_versions(self, obj=None):
        """Delete all versions from the current location downward"""
        if obj is None:
            obj = self # Silva Root
        for item in obj.aq_inner.objectValues():
            if IVersionedContent.isImplementedBy(item):
                pvs = item._previous_versions
                if not pvs is None:
                    while len(pvs) > 1:
                        # remove from list of previous versions and 
                        # from container (Document)
                        v = str(pvs.pop(0)[0])
                        if v in item.objectIds():
                            item.manage_delObjects([v])
                            print 'Removed old version %s/%s' % (item.absolute_url(), v)
            elif IContainer.isImplementedBy(item):
                self.delete_old_versions(item)
        return 'Done!'
        
InitializeClass(Root)

manage_addRootForm = PageTemplateFile("www/rootAdd", globals(),
                                      __name__='manage_addRootForm')

def create_published_demo_index(silva_root, title, REQUEST):
    silva_root.sec_update_last_author_info()
    silva_root.manage_addProduct['Silva'].manage_addDocument('index', title)
    doc = silva_root.index
    doc.sec_update_last_author_info()
    version = doc.get_editable()
    version.content.manage_edit('<doc><p type="normal">Welcome to Silva! This is the public view. To actually see something interesting, try adding \'/edit\' to your url (if you\'re not already editing, you can <link url="edit">click this link</link>).</p></doc>')
    doc.set_unapproved_version_publication_datetime(DateTime())
    doc.approve_version()

def manage_addRoot(self, id, title, REQUEST=None):
    """Add a Silva root."""
    # no id check possible or necessary, as this only happens rarely and the
    # Zope id check is fine
    object = Root(id)
    self._setObject(id, object)
    object = getattr(self, id)

    # now set it all up
    install.installFromScratch(object)

    # XXX no sample content this way as SilvaDocument is a separate
    # product now..needs to be fixed
    #create_published_demo_index(object, title, REQUEST)

    add_and_edit(self, id, REQUEST)
    return ''
