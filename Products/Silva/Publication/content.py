# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from App.special_dtml import DTMLFile
from App.class_init import InitializeClass
from zExceptions import BadRequest

# Silva
from Products.Silva import Folder
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.interfaces import (
    IPublication, IRoot, ISiteManager, IInvisibleService)
from silva.translations import translate as _


class OverQuotaException(BadRequest):
    """Exception triggered when you're overquota.
    """
    pass


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
    silvaconf.icon('www/silvapublication.gif')

    @property
    def manage_options(self):
        base_options = super(Publication, self).manage_options
        manage_options = (base_options[0], )
        if ISiteManager(self).is_site():
            manage_options += ({'label':'Services', 'action':'manage_services'},)
        return manage_options + base_options[1:]

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_main')
    manage_main = DTMLFile('folderContents', globals())

    security.declarePublic('objectItemsContents')
    def objectItemsContents(self, spec=None):
        """Don't display services by default in the Silva root.
        """
        return [item for item in super(Publication, self).objectItems()
                if not item[0].startswith('service_')]

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_services')
    manage_services = DTMLFile('folderServices', globals())

    security.declarePublic('objectItemsServices')
    def objectItemsServices(self, spec=None):
        """Display services separately.
        """
        return [item for item in super(Publication, self).objectItems()
                if item[0].startswith('service_')
                and not IInvisibleService.providedBy(item[1])]

    # MANIPULATORS

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'to_folder')
    def to_folder(self):
        """Publication becomes a folder instead.
        """
        self._to_folder_or_publication_helper(to_folder=1)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'validate_wanted_quota')
    def validate_wanted_quota(self, value, REQUEST=None):
        """Validate the wanted quota is correct the current
        publication.
        """
        if value < 0:
            return False        # Quota can't be negative.
        if (not value) or IRoot.providedBy(self):
            return True         # 0 means no quota, Root don't have
                                # any parents.
        parent = aq_parent(self).get_publication()
        quota = parent.get_current_quota()
        if quota and quota < value:
            return False
        return True

    def _verify_quota(self, REQUEST=None):
        quota = self.get_current_quota() * 1024 * 1024
        if quota and self.used_space > quota:
            excess = self.used_space - quota
            raise OverQuotaException(excess)

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_current_quota')
    def get_current_quota(self):
        """Return the current quota value on the publication.
        """
        service_metadata = self.service_metadata
        binding = service_metadata.getMetadata(self)
        try:
            return int(binding.get('silva-quota', element_id='quota') or 0)
        except KeyError:        # This publication object doesn't have
                                # this metadata set
            return aq_parent(self).get_current_quota()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_publication')
    def get_publication(self):
        """Get publication. Can be used with acquisition to get
        'nearest' Silva publication.
        """
        return self.aq_inner

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_transparent')
    def is_transparent(self):
        return 0


InitializeClass(Publication)


class PublicationAddForm(Folder.FolderAddForm):
    grok.context(IPublication)
    grok.name(u'Silva Publication')
