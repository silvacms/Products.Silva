# Copyright (c) 2003-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.cachedescriptors.property import CachedProperty
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from App.special_dtml import DTMLFile
from App.class_init import InitializeClass
from zExceptions import BadRequest
import Acquisition
import transaction

# Silva
from Products.Silva import Folder
from Products.Silva import SilvaPermissions

from silva.core.smi.interfaces import IPropertiesTab
from silva.core import conf as silvaconf
from silva.core.interfaces import (
    IPublication, IRoot, ISiteManager, IInvisibleService)
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction


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

    grok.implements(IPublication)
    silvaconf.priority(-5)
    silvaconf.icon('www/silvapublication.png')

    @property
    def manage_options(self):
        # A hackish way to get a Silva tab in between the standard ZMI tabs
        base_options = super(Publication, self).manage_options
        manage_options = (base_options[0], )
        if ISiteManager(self).isSite():
            manage_options += ({'label':'Services', 'action':'manage_services'},)
        return manage_options + base_options[1:]

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_main')
    manage_main = DTMLFile(
        'www/folderContents', globals())

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_services')
    manage_services = DTMLFile(
        'www/folderServices', globals())


    # MANIPULATORS

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
        quota = self.get_current_quota() * 1024 * 1024
        if quota and self.used_space > quota:
            excess = self.used_space - quota
            transaction.abort()
            raise OverQuotaException(excess)

    # ACCESSORS

    security.declarePublic('objectItemsContents')
    def objectItemsContents(self, spec=None):
        """Don't display services by default in the Silva root.
        """
        return [item for item in super(Publication, self).objectItems()
                if not item[0].startswith('service_')]

    security.declarePublic('objectItemsServices')
    def objectItemsServices(self, spec=None):
        """Display services separately.
        """
        return [item for item in super(Publication, self).objectItems()
                if item[0].startswith('service_')
                and not IInvisibleService.providedBy(item[1])]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_current_quota')
    def get_current_quota(self):
        """Return the current quota value on the publication.
        """
        service_metadata = self.service_metadata
        binding = service_metadata.getMetadata(self)
        try:
            return int(binding.get('silva-quota', element_id='quota') or 0)
        except KeyError:        # This publication object doesn't have
                                # this metadata set
            return self.aq_parent.get_current_quota()

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


class ManageLocalSite(silvaforms.SMIForm):
    """This form let enable (or disable) a Publication as a local
    site.
    """
    grok.name('tab_localsite')
    grok.require('zope2.ViewManagementScreens')
    grok.implements(IPropertiesTab)

    label = _(u"Local site")
    description = _(u"Here you can enable/disable a local site (or subsite). "
                    u"By making a local site, you will be able to add "
                    u"local services to the publication. Those services "
                    u"will only affect elements inside that publication.")

    @CachedProperty
    def manager(self):
        return ISiteManager(self.context)

    def can_be_a_local_site(self):
        return IPublication.providedBy(self.context) and \
            not self.manager.isSite()

    @silvaforms.action(
        _("make local site"),
        identifier="make_site",
        available=lambda form: form.can_be_a_local_site())
    def make_site(self):
        try:
            self.manager.makeSite()
        except ValueError, e:
            self.send_message(str(e), type=u"error")
            return silvaforms.FAILURE
        else:
            self.send_message(_("Local site activated."), type=u"feedback")
            return silvaforms.SUCCESS

    def can_be_normal_again(self):
        return IPublication.providedBy(self.context) and \
            self.manager.isSite() and \
            not IRoot.providedBy(self.context)

    @silvaforms.action(
        _("remove local site"),
        identifier="delete_site",
        available=lambda form: form.can_be_normal_again(),
        implements=IRemoverAction)
    def delete_site(self):
        try:
            self.manager.deleteSite()
        except ValueError, e:
            self.send_message(str(e), type=u"error")
            return silvaforms.FAILURE
        else:
            self.send_message(_("Local site deactivated."), type=u"feedback")
            return silvaforms.SUCCESS


class PublicationAddForm(Folder.FolderAddForm):
    grok.context(IPublication)
    grok.name(u'Silva Publication')
