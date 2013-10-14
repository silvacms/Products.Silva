# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from App.special_dtml import DTMLFile
from App.class_init import InitializeClass
from zExceptions import BadRequest
from zope.component import getUtility

# Silva
from Products.Silva.Folder import Folder, FolderAddForm
from Products.Silva import SilvaPermissions, helpers

from silva.core import conf as silvaconf
from silva.core.interfaces import IPublication, ISiteManager, IInvisibleService
from silva.core.interfaces import ContentError
from silva.core.services.interfaces import IMetadataService
from silva.translations import translate as _


class OverQuotaException(BadRequest):
    """Exception triggered when you're overquota.
    """
    pass


class Publication(Folder):
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
    silvaconf.icon('icons/publication.gif')

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
        helpers.convert_content(self, Folder)

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'to_publication')
    def to_publication(self):
        raise ContentError(
            _(u"You cannot convert a publication into a publication."), self)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'validate_wanted_quota')
    def validate_wanted_quota(self, value, REQUEST=None):
        """Validate the wanted quota is correct the current
        publication.
        """
        if value < 0:
            # Quota can't be negative.
            return False
        if not value:
            # 0 or means no quota.
            return True
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
        binding = getUtility(IMetadataService).getMetadata(self)
        try:
            local = int(binding.get('silva-quota', element_id='quota') or 0)
            if local > 0:
                return local
        except KeyError:
            pass
        # Test parent publication/root.
        parent = aq_parent(self)
        return parent.get_current_quota()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_publication')
    def get_publication(self):
        """Get publication. Can be used with acquisition to get
        'nearest' Silva publication.
        """
        return aq_inner(self)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_transparent')
    def is_transparent(self):
        return 0


InitializeClass(Publication)


class PublicationAddForm(FolderAddForm):
    grok.context(IPublication)
    grok.name(u'Silva Publication')
