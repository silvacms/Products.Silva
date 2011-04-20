# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from OFS.interfaces import IObjectWillBeRemovedEvent

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.SilvaObject import TitledObject
from Products.SilvaMetadata.Exceptions import BindingError
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.translations import translate as _
from silva.core.interfaces import IVersionManager
from silva.core.interfaces import IVersion, VersioningError
from silva.core.services.interfaces import ICataloging


class Version(TitledObject, SimpleItem):
    """A Version of a versioned content.
    """
    grok.implements(IVersion)

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id
        self._v_creation_datetime = DateTime()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_version')
    def get_version(self):
        """Returns itself. Used by acquisition to get the
           neared version.
        """
        return self.aq_inner


InitializeClass(Version)


class VersionManager(grok.Adapter):
    """Adapter to manage Silva versions
    """
    grok.implements(IVersionManager)
    grok.provides(IVersionManager)
    grok.context(IVersion)

    def __init__(self, version):
        self.version = version
        self.content = version.get_content()

    def make_editable(self):
        """Make the version editable.
        """
        approved_version = self.content.get_approved_version(False)
        if approved_version is not None:
            raise VersioningError(_('An approved version is already available'))

        current_version = self.content.get_unapproved_version(False)
        if current_version is not None:
            # move the current editable version to _previous_versions
            if self.content.is_approval_requested():
                raise VersioningError(_('A version is waiting approval'))

            version_tuple = self.content._unapproved_version
            if self.content._previous_versions is None:
                self.content._previous_versions = []
            self.content._previous_versions.append(version_tuple)
            # XXX should be event
            self.content._unindex_version(current_version)

        new_version_id = self.content.get_new_version_id()
        self.content.manage_clone(self.version, new_version_id)
        self.content._unapproved_version = (new_version_id, None, None)
        self.content._index_version(new_version_id)
        return True

    def delete(self):
        """Delete the version
        """
        versionid = self.version.id

        if self.content.get_approved_version(False) == versionid:
            raise VersioningError(_(u"Version is approved"))
        if self.content.get_public_version(False) == versionid:
            raise VersioningError(_(u"Version is published"))

        if self.content.get_unapproved_version(False) == versionid:
            self.content._unapproved_version = (None, None, None)
        else:
            for version in self.content._previous_versions:
                if version[0] == versionid:
                    self.content._previous_versions.remove(version)
        self.content.manage_delObjects([versionid])
        return True

    def get_modification_datetime(self):
        return getUtility(IMetadataService).getMetadataValue(
            self.version, 'silva-extra', 'modificationtime')

    def __get_version_tuple(self):
        versionid = self.version.id
        if self.content.get_unapproved_version(False) == versionid:
            return self.content._unapproved_version
        elif self.content.get_approved_version(False) == versionid:
            return self.content._approved_version
        elif self.content.get_public_version(False) == versionid:
            return self.content._public_version
        elif self.content._previous_versions:
            for info in self.context._previous_versions:
                if info[0] == versionid:
                    return info
        return (None, None, None)

    def get_publication_datetime(self):
        return self.__get_version_tuple()[1]

    def get_expiration_datetime(self):
        return self.__get_version_tuple()[2]

    def get_last_author(self):
        return self.content.sec_get_last_author_info(self.version)

    def get_status(self):
        """Returns the status of a version as a string

            return value can be one of the following strings:

                unapproved
                pending
                approved
                published
                last_closed
                closed
        """
        versionid = self.version.id
        if self.content.get_unapproved_version(False) == versionid:
            if self.content.is_approval_requested():
                return 'pending'
            return 'unapproved'
        elif self.content.get_approved_version(False) == versionid:
            return 'approved'
        elif self.content.get_public_version(False) == versionid:
            return 'published'
        else:
            if self.content._previous_versions:
                if self.content._previous_versions[-1][0] == versionid:
                    return 'last_closed'
                else:
                    for (vid, vpt, vet) in self.content._previous_versions:
                        if vid == versionid:
                            return 'closed'
        raise VersioningError(
            _('No such version ${version}',
              mapping={'version': versionid}))


_i18n_markers = (_('unapproved'), _('approved'), _('last_closed'),
                 _('closed'), _('draft'), _('pending'), _('public'),)


@grok.subscribe(IVersion, IObjectModifiedEvent)
def version_modified(version, event):
    # This version have been modified
    version.get_content().sec_update_last_author_info()


@grok.subscribe(IVersion, IObjectWillBeRemovedEvent)
def catalog_version_removed(version, event):
    if version != event.object:
        # Only interested about version removed by hand.
        return
    ICataloging(version).unindex()


@grok.subscribe(IVersion, IObjectMovedEvent)
def version_moved(version, event):
    if version != event.object or IObjectRemovedEvent.providedBy(event):
        return
    timings = {}
    ctime = getattr(version, '_v_creation_datetime', None)
    if ctime is None:
        return
    try:
        binding = getUtility(IMetadataService).getMetadata(version)
    except BindingError:
        return
    if binding is None:
        return
    for elem in ('creationtime', 'modificationtime'):
        old = binding.get('silva-extra', element_id=elem)
        if old is None:
            timings[elem] = ctime
    binding.setValues('silva-extra', timings)
