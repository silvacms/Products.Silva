# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.70 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Silva
import Folder
import SilvaPermissions
import ContainerPolicy
# misc
from helpers import add_and_edit

from Products.Silva.ImporterRegistry import get_importer, xml_import_helper, get_xml_id, get_xml_title
from Products.Silva.Metadata import export_metadata
from Products.Silva import mangle
from Products.Silva.i18n import translate as _

from interfaces import IPublication, IRoot

from zExceptions import BadRequest
import transaction
import Acquisition

class OverQuotaException(BadRequest):
    """Exception triggered when you're overquota.
    """
    pass

class AcquisitionMethod(Acquisition.Explicit):
    """This class let you have an acquisition context on a method.
    """
    def __init__(self, parent, method_name):
        self.parent = parent
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        instance = self.parent.aq_inner
        method = getattr(instance, self.method_name)
        return method(*args, **kwargs)


class Publication(Folder.Folder):
    __doc__ = _("""Publications are special folders. They function as the 
       major organizing blocks of a Silva site. They are comparable to 
       binders, and can contain folders, documents, and assets. 
       Publications are opaque. They instill a threshold of view, showing
       only the contents of the current publication. This keeps the overview
       screens manageable. Publications have configuration settings that
       determine which core and pluggable objects are available. For
       complex sites, sub-publications can be nested.
    """)
    security = ClassSecurityInfo()
    
    meta_type = "Silva Publication"

    implements(IPublication)

    _addables_allowed_in_publication = None

    def __init__(self, id):
        Publication.inheritedAttribute('__init__')(
            self, id)
    
    # MANIPULATORS
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_silva_addables_allowed_in_publication')
    def set_silva_addables_allowed_in_publication(self, addables):
        self._addables_allowed_in_publication = addables
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Publication becomes a folder instead.
        """
        self._to_folder_or_publication_helper(to_folder=1)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'validate_wanted_quota')
    def validate_wanted_quota(self, value, REQUEST=None):
        """Validate the wanted quota is correct the current
        publication.
        """
        if value < 0:
            return False        # Quota can't be negative.
        if (not value) or IRoot.providedBy(self):
            return True         # 0 means no quota, Root don't have
                                # any parents.
        parent = self.aq_parent.get_publication()
        quota = parent.get_current_quota()
        if quota and quota < value:
            return False
        return True

    def get_wanted_quota_validator(self):
        """Return the quota validator with an acquisition context
        (needed to be used in Formulator).
        """
        return AcquisitionMethod(self, 'validate_wanted_quota')


    def _verify_quota(self, REQUEST=None):

        quota = self.get_current_quota()
        if quota and self.used_space > (quota * 1024 * 1024):
            # No comments.
            if (not REQUEST) and hasattr(self, 'REQUEST'):
                REQUEST = self.REQUEST
            if REQUEST:
                transaction.abort()
                REQUEST.form.clear()
                REQUEST.form['message_type'] = 'error'
                REQUEST.form['message'] = _('You are overquota.')
                REQUEST.RESPONSE.write(unicode(REQUEST.PARENTS[0].index_html()).encode('utf-8'))
                raise OverQuotaException
            else:
                raise RuntimeError, "Overquota"

        
    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_current_quota')
    def get_current_quota(self):
        """Return the current quota value on the publication.
        """
        service_metadata = self.service_metadata
        binding = service_metadata.getMetadata(self)
        return int(binding.get('silva-quota', element_id='quota') or 0)
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_publication')
    def get_publication(self):
        """Get publication. Can be used with acquisition to get
        'nearest' Silva publication.
        """
        return self.aq_inner
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_transparent')
    def is_transparent(self):
        return 0

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
        f = context.f
        f.write('<silva_publication id="%s">' % self.id)
        self._to_xml_helper(context)
        export_metadata(self, context)
        f.write('</silva_publication>')

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_addables_allowed_in_publication')
    def get_silva_addables_allowed_in_publication(self):
        current = self
        root = self.get_root()
        while 1:
            if IPublication.providedBy(current):
                addables = current._addables_allowed_in_publication
                if addables is not None:
                    return addables
            if current == root:
                return self.get_silva_addables_all()
            current = current.aq_parent

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_silva_addables_acquired')
    def is_silva_addables_acquired(self):
        return self._addables_allowed_in_publication is None
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_document_chapter_links')
    def get_document_chapter_links(self, depth=0):
        """returns a dict for document links (accessibility).

        This will return chapter, section, subsection and subsubsection
        links in a dictionary.
        
        These can be used by Mozilla in the accessibility toolbar.
        """
        types = ['chapter', 'section', 'subsection', 'subsubsection']

        result = {}
        tree = self.get_container_tree(depth)
        for depth, container in tree:
            if not container.is_published():
                continue
            if not result.has_key(types[depth]):
                result[types[depth]] = []
            result[types[depth]].append({
                'title': container.get_title(),
                'url': container.absolute_url()
                })
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_document_index_links')
    def get_document_index_links(self, toc_id='index', index_id=None):
        """Returns a dictionary for document links.

        This will return the contents and index links, if
        available.

        These can be used by Mozilla in the accessibility toolbar.
        """
        result = {}
        # get the table of contents
        contents = self._getOb(toc_id, None)
        if contents is not None and contents.is_published():
            result['contents'] = contents.absolute_url()
   
        # get the index
        if index_id is None:
            indexers = self.objectValues(['Silva Indexer'])
            if indexers:
                index = indexers[0]
            else:
                index = None
        else:
             index = self._getOb(index_id, None)

        if index is not None and index.is_published():
            result['index'] = index.absolute_url()
        
        return result

InitializeClass(Publication)

def manage_addPublication(
    self, id, title, create_default=1, policy_name='None', REQUEST=None):
    """Add a Silva publication."""
    if not mangle.Id(self, id).isValid():
        return
    object = Publication(id)
    self._setObject(id, object)
    object = getattr(self, id)
    object.set_title(title)
    if create_default:
        policy = self.service_containerpolicy.getPolicy(policy_name)
        policy.createDefaultDocument(object, title)
    add_and_edit(self, id, REQUEST)
    return ''

def xml_import_handler(object, node):
    """import publication"""
    
    def factory(object, id, title):
        object.manage_addProduct["Silva"].manage_addPublication(id, title, 0)
    
    return Folder.xml_import_handler(object, node, factory=factory)
        
