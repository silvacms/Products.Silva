# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.36 $
# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from DateTime import DateTime
# Silva interfaces
from IPublication import IPublication
# Silva
from Publication import Publication
import SilvaPermissions
import install
# misc
from helpers import add_and_edit

icon="globals/silva.gif"

class Root(Publication):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Root"

    __implements__ = IPublication

    # MANIPULATORS

    def manage_afterAdd(self, item, container):
        # since we're root, we don't want to notify our container
        pass
        
    def manage_beforeDelete(self, item, container):
        # since we're root, we don't want to notify our container
        pass

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Don't do anything here. Can't do this with root.
        """
        pass
    
    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_root')
    def get_root(self):
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        return self.aq_inner

    # FIXME: should be renamed to something else, indicating we get a url
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'silva_root')
    def silva_root(self):
        """Get url of root of site.
        """
        return self.aq_inner.absolute_url()
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
        f = context.f
        f.write('<silva_root id="%s">' % self.id)
        self._to_xml_helper(context)
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

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'upgrade_silva')
    def upgrade_silva(self, from_version='0.8.5'):
        """Upgrade Silva from previous version.
        """
        if from_version != '0.8.5':
            raise "Not supported", "Upgrading from another version than 0.8.5 is not supported."
        import upgrade
        my_id = self.id
        missing_ids = upgrade.from085to086(self.aq_inner.aq_parent, self)
        if missing_ids:
            missing_ids.sort()
            msg = 'You may want to copy over the objects with the following ids by hand:<ul>%s</ul>' \
                  % '\r\n'.join([ '<li>%s</li>' % id for id in missing_ids ])
        else:
            msg = ''
        return "Upgrade of &laquo;%s&raquo; succeeded.<br /> A backup is in &laquo;%s_085&raquo;.<br /> %s" \
               % (my_id, my_id, msg)
    
InitializeClass(Root)

manage_addRootForm = PageTemplateFile("www/rootAdd", globals(),
                                      __name__='manage_addRootForm')

def create_published_demo_index(silva_root, title):
    silva_root.manage_addProduct['Silva'].manage_addDocument('index', title)
    doc = silva_root.index
    version = doc.get_editable()
    version.manage_edit('<doc><p type="normal">Welcome to Silva! This is the public view. To actually see something interesting, try adding \'/edit\' to your url (if you\'re not already editing, you can <link url="edit">click this link</link>).</p></doc>')
    doc.set_unapproved_version_publication_datetime(DateTime())
    doc.approve_version()

def manage_addRoot(self, id, title, REQUEST=None):
    """Add a Silva root."""
    # no id check possible or necessary, as this only happens rarely and the
    # Zope id check is fine
    object = Root(id, title)
    self._setObject(id, object)
    object = getattr(self, id)

    create_published_demo_index(object, title)

    # now set it all up
    install.installFromScratch(object)

    add_and_edit(self, id, REQUEST)
    return ''
