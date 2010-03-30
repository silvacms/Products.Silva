# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from OFS.Folder import Folder as BaseFolder
from Persistence import Persistent
from zExceptions import NotFound

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Versioning import Versioning
from Products.Silva.Content import Content

from silva.core.interfaces import IVersionedContent, ICatalogedVersionedContent
from silva.core.services.catalog import Cataloging
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes
from silva.core.views.interfaces import IPreviewLayer

# Silva adapters
from Products.Silva.adapters.virtualhosting import getVirtualHostingAdapter


class CachedData(Persistent):
    """ Persistent cache container
    """
    def __init__(self, data, datetime):
        self.data = data
        self.datetime = datetime


class VersionedContent(Content, Versioning, BaseFolder):
    security = ClassSecurityInfo()

    grok.implements(IVersionedContent)
    grok.baseclass()

    # there is always at least a single version to start with,
    # created by the object's factory function
    _version_count = 1
    # for backwards compatibilty - ugh.
    _cached_checked = {}
    _cached_data = {}

    # Set ZMI tabs
    manage_options = (
        (BaseFolder.manage_options[0], ) +
        ({'label': 'Silva /edit...', 'action':'edit'},)+
        BaseFolder.manage_options[1:])

    def __init__(self, id):
        """Initialize VersionedContent.
        """
        super(VersionedContent, self).__init__(id)
        self._cached_data = {}
        self._cached_checked = {}

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set title of version under edit.
        """
        editable = self.get_editable()
        if editable is None:
            return
        editable.set_title(title)
        if self.id == 'index':
            container = self.get_container()
            container._invalidate_sidebar(container)

    # ACCESSORS
    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """Check to see if the title can be set
        """
        return not not self.get_editable()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                             'get_title')
    def get_title(self):
        """Get title for public use, from published version.
        """
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
        return viewable.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_editable')
    def get_title_editable(self):
        """Get title for editable or previewable use
        """
        # Ask for 'previewable', which will return either the 'next version'
        # (which may be under edit, or is approved), or the public version,
        # or, as a last resort, the closed version.
        # This to be able to show at least some title in the Silva edit
        # screens.
        previewable = self.get_previewable()
        if previewable is None:
            return "[No title available]"
        return previewable.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_or_id_editable')
    def get_title_or_id_editable(self):
        """Get title or id editable or previewable use.
        """
        title = self.get_title_editable()
        if title.strip() == '':
            return self.id
        else:
            return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short_title for public use, from published version.
        """
        # Analogous to get_title
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
        return viewable.get_short_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title_editable')
    def get_short_title_editable(self):
        """Get short_title for editable or previewable use
        """
        # Analogous to get_title_editable
        previewable = self.get_previewable()
        if previewable is None:
            return "[No (short) title available]"
        return previewable.get_short_title()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_editable')
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        # the editable version is the unapproved version
        version_id = self.get_unapproved_version()
        if version_id is None:
            return None # there is no editable version
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_previewable')
    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        version_id = self.get_next_version()
        if version_id is None:
            version_id = self.get_public_version()
            if version_id is None:
                version_id = self.get_last_closed_version()
                if version_id is None:
                    return None
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_viewable')
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        version_id = self.get_public_version()
        if version_id is None:
            return None # There is no public document
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_last_closed')
    def get_last_closed(self):
        """Get the last closed version (may be the object itself if
        no versioning).
        """
        version_id = self.get_last_closed_version()
        if version_id is None:
            return None # There is no public document
        return getattr(self, version_id)

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'view_version')
    def view_version(self, version=None):
        version_name = self.REQUEST.other.get('SILVA_PREVIEW_NAME', '')
        if version_name:
            version = getattr(self, version_name, None)
            if version is None:
                raise NotFound(version_name)
        return super(VersionedContent, self).view_version(version)

    security.declareProtected(SilvaPermissions.View, 'view')
    def view(self):
        """
        """
        # XXX the "suppress_title" hack in the
        # SilvaDocument widget/top/doc/mode_view
        # makes it necessary to bypass the cache here
        if self.REQUEST.other.get('suppress_title'):
            return VersionedContent.inheritedAttribute('view')(self)

        if IPreviewLayer.providedBy(self.REQUEST):
            # Preview, don't pay attention to the cache.
            return VersionedContent.inheritedAttribute('view')(self)

        adapter = getVirtualHostingAdapter(self)
        cache_key = ('public', adapter.getVirtualHostKey())
        data = self._get_cached_data(cache_key)
        if data is not None:
            return data

        # No cache or not valid anymore, so render.
        data = VersionedContent.inheritedAttribute('view')(self)
        # See if the previous cacheability check is still valid,
        # if not, see if we can cache at all.
        publicationtime = self.get_public_version_publication_datetime()
        refreshtime = self.service_extensions.get_refresh_datetime()
        cache_check_time = self._cached_checked.get(cache_key, None)
        if (cache_check_time <= publicationtime or
                cache_check_time <= refreshtime):
            if self.is_cacheable():
                # Caching the data is allowed.
                now = DateTime()
                self._cached_data[cache_key] = CachedData(data, now)
                self._cached_checked[cache_key] = now
                self._p_changed = 1
            else:
                # Remove from cache if caching is not allowed
                # or not valid anymore.
                # Only remove if there is something to remove,
                # avoiding creating a transaction each time.
                if self._cached_data.has_key(cache_key):
                    del self._cached_data[cache_key]
                    self._p_changed = 1
        return data

    def _get_cached_data(self, cache_key):
        cached_data = self._cached_data.get(cache_key, None)
        if cached_data is not None:
            # If cache is still valid, serve it.
            # XXX: get_public_version_publication_datetime *and*
            # is_version_published trigger workflow updates; necessary?
            data, datetime = cached_data.data, cached_data.datetime
            publicationtime = self.get_public_version_publication_datetime()
            if datetime > publicationtime:
                refreshtime = self.service_extensions.get_refresh_datetime()
                if (datetime > refreshtime and self.is_version_published()):
                    # Yes! We have valid cached data! Return data
                    return data
        return None

    def _clean_cache(self):
        self._cached_data = {}
        self._cached_checked = {}

    security.declareProtected(SilvaPermissions.View, 'is_cached')
    def is_cached(self, view_type='public'):
        adapter = getVirtualHostingAdapter(self)
        cache_key = (view_type, adapter.getVirtualHostKey())
        return self._get_cached_data(cache_key) is not None

    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if the result of the view method can be safely
        cached.
        """
        # by default nothing is safely cacheable
        return 0


InitializeClass(VersionedContent)

class CatalogedVersionedContent(VersionedContent):
    """VersionedContent from those versions are in the catalog.
    """
    grok.implements(ICatalogedVersionedContent)
    grok.baseclass()

    def _index_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).index()

    def _reindex_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).reindex()

    def _unindex_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).unindex()

InitializeClass(CatalogedVersionedContent)


class VersionedContentCataloging(Cataloging):
    """Cataloging support for versioned content.
    """
    grok.context(ICatalogedVersionedContent)

    def get_indexable_versions(self):
        version_ids = [
            self.context.get_next_version(),
            self.context.get_public_version(),]
        for version_id in version_ids:
            if version_id is None:
                continue
            if hasattr(self.context.aq_base, version_id):
                yield getattr(self.context, version_id, None)

    def index(self, indexes=None):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).index(indexes=indexes)
        for version in self.get_indexable_versions():
            attributes = ICatalogingAttributes(version)
            path = '/'.join((self._path, version.getId(),))
            self._catalog.catalog_object(attributes, path)

    def unindex(self):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).unindex()
        for version in self.get_indexable_versions():
            path = '/'.join((self._path, version.getId(),))
            self._catalog.uncatalog_object(path)
