# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.68 $

# Python
from StringIO import StringIO

from zope.interface import implements

# Zope
from OFS import Folder
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from DateTime import DateTime
from Persistence import Persistent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
import SilvaPermissions
from Versioning import Versioning
from Content import Content
from Versioning import VersioningError
import mangle
# Silva adapters
from Products.Silva.adapters.virtualhosting import getVirtualHostingAdapter
# Silva interfaces
from interfaces import IVersionedContent

from webdav.common import PreconditionFailed, Conflict
from zExceptions import Forbidden

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

    implements(IVersionedContent)

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

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'public_preview')
    def public_preview(self):
        """Override public preview to add back and publish now button.
        """
        # this is a bit nasty: to allow displaying some additional buttons
        # in preview mode (the 'back' and 'publish now' ones) we add
        # some HTML to the result before sending it to the browser
        preview_buttons = PageTemplateFile(
            'www/preview_buttons', globals(),
            __name__ = 'preview_buttons').__of__(self)

        REQUEST = self.REQUEST
        SESSION = REQUEST.SESSION
        
        # have to make sure the clients don't cache the public preview page
        # because of the back button
        # XXX copied from view/set_cache_headers.py, loading stuff from the
        # views is somewhat messy... but perhaps i should have done that 
        # anyway?
        response = REQUEST.RESPONSE
        headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
                    ('Last-Modified', 
                        DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
                    ('Cache-Control', 'no-cache, must-revalidate'),
                    ('Cache-Control', 'post-check=0, pre-check=0'),
                    ('Pragma', 'no-cache'),
                    ]

        placed = []
        for key, value in headers:
            if key not in placed:
                response.setHeader(key, value)
                placed.append(key)
            else:
                response.addHeader(key, value)
                
        # make sure the back button points to the last edit screen visited
        back_url = SESSION.get('public_preview_back_url', None)
        # [sic]
        referer = REQUEST.get('HTTP_REFERER', None)
        if (referer and 'edit' in referer.split('/') and 
                not referer.endswith('/public_html')):
            # set the referer as the target for the back button...
            SESSION['public_preview_back_url'] = referer
            back_url = referer

        # check whether this should have a publish now button
        show_publish_now = (
            self.get_unapproved_version() is not None and
            getSecurityManager().checkPermission(
            'Approve Silva content', self))

        # prepare arguments for preview_buttons page template
        args = {
            'message': REQUEST.get('message', ''),
            'message_type': REQUEST.get('message_type', ''),
            'show_publish_now': show_publish_now,
            'back_url': back_url,
            }
        # now render html
        buttonhtml = preview_buttons(**args)
        # XXX yuck, this doesn't deliver valid HTML by definition..
        return '%s%s' % (self.preview(), buttonhtml)
    
    security.declareProtected(SilvaPermissions.View, 'view')
    def view(self):
        """
        """
        # XXX the "suppress_title" hack in the
        # SilvaDocument widget/top/doc/mode_view
        # makes it necessary to bypass the cache here
        if self.REQUEST.other.get('suppress_title'):
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

    # WebDAV API
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'DELETE')
    def DELETE(self):
        """DELETE support"""
        parent = self.aq_parent.aq_inner
        if not parent.is_delete_allowed(self.id):
            raise PreconditionFailed, ('Deleting this object is not allowed '
                                        'due to its workflow state')
        parent.action_delete([self.id])

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                                'COPY')
    def COPY(self):
        """COPY support"""
        # perform checks and (if required) remove object to overwrite
        parent, newid = self.copy_move_helper()
        # now do the actual copy
        self.aq_parent.aq_inner.action_copy([self.id], self.REQUEST)
        result = parent.aq_inner.manage_pasteObjects(self.REQUEST['__cp'])
        # so the object is copied now, but the id is not right: it's the same
        # as that of the original one, unless Zope mangled it, check the return
        # value for the new id and then move the object
        temp_id = result[0]['new_id']
        parent.action_rename(temp_id, newid)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'MOVE')
    def MOVE(self):
        """MOVE support"""
        if not self.aq_parent.aq_inner.is_delete_allowed(self.id):
            raise PreconditionFailed, 'object can not be deleted'
        # perform checks and (if required) remove object to overwrite
        parent, newid = self.copy_move_helper()
        # now do the actual move
        self.aq_parent.aq_inner.action_cut([self.id], self.REQUEST)
        result = parent.aq_inner.manage_pasteObjects(self.REQUEST['__cp'])
        # so the object is copied now, but the id is not right: it's the same
        # as that of the original one, unless Zope mangled it, check the return
        # value for the new id and then move the object
        temp_id = result[0]['new_id']
        parent.action_rename(temp_id, newid)

    def copy_move_helper(self):
        """helper method for COPY and MOVE
        
            If the 'overwrite' header is set, will remove any content that
            is currently located on the paste location, and raises an
            appropriate exception if anything goes wrong. If this passes it
            returns the physical path of the paste location.
        """
        # this is a lot more work than I reckon would be necessary due to
        # Zope's 'geared towards TTW usage' attitude...
        destination = self.REQUEST.get_header('destination')
        path = self.REQUEST.physicalPathFromURL(destination)
        parentpath = path[:-1]
        parent = self.restrictedTraverse(parentpath)
        newlocid = path[-1]
        isvalid = mangle.Id(parent, newlocid, allow_dup=1).isValid()
        if not isvalid:
            raise Forbidden, 'invalid destination id'
        old = self.restrictedTraverse(path, None)
        oldexists = (old is not None and old.getPhysicalPath() == tuple(path))
        secman = getSecurityManager()
        if self.REQUEST.get_header('overwrite') == 'T':
            # should delete the location (if it exists and the user is allowed
            # to do so)
            if oldexists:
                if not parent.is_delete_allowed(newlocid):
                    raise PreconditionFailed, 'could not delete old object'
                # see if the user has both permission to remove the object,
                # *and* the permission to add the replacement (else the old
                # object on the location is gone but the new one isn't placed)
                is_allowed = (secman.checkPermission(
                                    SilvaPermissions.ChangeSilvaContent,
                                    old) and 
                                secman.checkPermission(
                                    SilvaPermissions.ChangeSilvaContent,
                                    parent))
                if not is_allowed:
                    raise PreconditionFailed, ('overwriting old object not '
                                                'allowed')
                parent.action_delete([newlocid])
        else:
            # if there's an old object already on the copy location, bail out
            if oldexists:
                raise PreconditionFailed, 'target URL already exists'
        # see if we're allowed to copy the object to the parent folder
        is_allowed = secman.checkPermission(
                                SilvaPermissions.ChangeSilvaContent,
                                parent)
        if not is_allowed:
            # should we raise Unauthorized here instead?
            raise PreconditionFailed, ('you do not have the write '
                                        'permission in the copy location')

        return parent, newlocid

InitializeClass(VersionedContent)

class CatalogedVersionedContent(VersionedContent):
    """This class merely exists to mix VersionedContent with CatalogedVersioning
    """

    default_catalog = 'service_catalog'

    def manage_afterAdd(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_afterAdd')(
            self, item, container)
        self.indexVersions()

    def manage_beforeDelete(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_beforeDelete')(
            self, item, container)
        self.unindexVersions()
    
    def indexVersions(self):
        for version in self._get_indexable_versions():
            version.index_object()

    def unindexVersions(self):
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

