# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.58 $

# Python
from StringIO import StringIO

# Zope
from OFS import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime
from Persistence import Persistent
# Silva
import SilvaPermissions
from Versioning import Versioning
from Content import Content
from Versioning import VersioningError
# Silva adapters
from Products.Silva.adapters.virtualhosting import getVirtualHostingAdapter
# Silva interfaces
from interfaces import IVersionedContent

class CachedData(Persistent):
    """ Persistent cache container
    """
    def __init__(self, data, datetime):
        self.data = data
        self.datetime = datetime

class VersionedContent(Content, Versioning, Folder.Folder):
    security = ClassSecurityInfo()
    
    # there is always at least a single version to start with,
    # created by the object's factory function
    _version_count = 1

    __implements__ = IVersionedContent

    # for backwards compatibilty - ugh.
    _cached_checked = {}
    _cached_data = {}

    def __init__(self, id):
        """Initialize VersionedContent.

        VersionedContent has no title of its own; its versions do.
        """
        VersionedContent.inheritedAttribute('__init__')(
            self, id, '[VersionedContent title bug]')
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
        SilvaPermissions.ChangeSilvaContent, 'can_set_title')    
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
                              'sec_get_last_author_userid')
    def sec_get_last_author_userid(self):
        """Ask last userid of current transaction under edit.
        If it doesn't exist, get published version, or last closed.
        """
        version_id = (self.get_next_version() or
                      self.get_public_version() or
                      self.get_last_closed_version())
        # get the last transaction
        last_transaction = getattr(self,
                                   version_id).undoable_transactions(0, 1)
        if len(last_transaction) == 0:
            return None
        return last_transaction[0]['user_name']
                                        
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

    security.declareProtected(SilvaPermissions.View, 'view')
    def view(self, view_type='public'):
        """
        """
        # XXX view_type=edit or add does not work anyway, but...
        if view_type in ('edit','add'):
            return VersionedContent.inheritedAttribute('view')(
                self, view_type)
        
        # XXX the "suppress_title" hack in the
        # SilvaDocument widget/top/doc/mode_view
        # makes it necessary to bypass the cache here
        if self.REQUEST.other.get('suppress_title'):
            return VersionedContent.inheritedAttribute('view')(
                self, view_type)
        
        adapter = getVirtualHostingAdapter(self)
        cache_key = (view_type, adapter.getVirtualHostKey())
        
        data = self._get_cached_data(cache_key)
        if data is not None:
            return data

        # No cache or not valid anymore, so render.
        content = self.get_viewable()
        if content is None:
            return "Sorry, this document is not published yet."
        renderer_name = self.service_metadata.getMetadataValue(
            content, "silva-extra", "renderer_name")

        if not renderer_name or renderer_name == "(Default)":
            renderer_name = self.service_renderer_registry.getDefaultRendererNameForMetaType(content.meta_type)
            
        if renderer_name and renderer_name != "Normal View (XMLWidgets)":
            renderer = self.service_renderer_registry.getRendererByName(
                renderer_name, 'Silva Document Version')
            data = renderer.render(content)
        else:
            # XXX: a hack to call back into the old XML widgets way
            # of rendering. done like so because the old system is
            # hard to follow, and thus practicality does indeed trump
            # purity sometimes. :)
            data = VersionedContent.inheritedAttribute('view')(self, view_type)
        
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
    """This class merely exists to mix VersionedContent with CatalogedVersioning
    """

    default_catalog = 'service_catalog'

    def manage_afterAdd(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_afterAdd')(
            self, item, container)
        for version in self._get_indexable_versions():
            version.index_object()

    def manage_beforeDelete(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_beforeDelete')(
            self, item, container)
        for version in self._get_indexable_versions():
            version.unindex_object()

    def _get_indexable_versions(self):
        version_ids = [self.get_next_version(),
                       self.get_public_version()]
        result = []
        for version_id in version_ids:
            if version_id is None:
                continue
            if hasattr(self.aq_base, version_id):
                version = getattr(self, version_id, None)
                result.append(version)
        return result

    def _index_version(self, version_id):
        # python2.2 and up compatibility check:
        if version_id is None:
            return
        version = getattr(self, version_id, None)
        if version is not None:
            version.index_object()
        
    def _reindex_version(self, version_id):
        # python2.2 and up compatibility check:
        if version_id is None:
            return
        version = getattr(self, version_id, None)
        if version is not None:
            version.reindex_object()

    def _unindex_version(self, version_id):
        # python2.2 and up compatibility check:
        if version_id is None:
            return
        version = getattr(self, version_id, None)
        if version is not None:
            version.unindex_object()
        
InitializeClass(CatalogedVersionedContent)

