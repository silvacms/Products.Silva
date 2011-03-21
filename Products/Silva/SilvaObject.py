# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


# Zope 3
from five import grok
from zope import component
from zope.container.interfaces import IContainerModifiedEvent
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.traversing.browser import absoluteURL

# Zope 2
from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from Acquisition import aq_base, aq_inner
from App.class_init import InitializeClass
from DateTime import DateTime
from OFS.interfaces import IObjectClonedEvent
from OFS.interfaces import IObjectWillBeAddedEvent
from OFS.interfaces import IObjectWillBeMovedEvent

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Security import Security

# Silva adapters
from Products.SilvaMetadata.Exceptions import BindingError
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core.services.interfaces import ICataloging
from silva.core.views.interfaces import IPreviewLayer
from silva.translations import translate as _

from silva.core.interfaces import (
    ISilvaObject, IPublishable, IContent, IRoot, IVersionedContent)


class TitledObject(object):
    """Object with a Title stored in the metadata.
    """
    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_title')
    def set_title(self, title):
        """Set the title of the silva object.
        """
        # FIXME: Ugh. I get unicode from formulator but this will not validate
        # when using the metadata system. So first make it into utf-8 again..
        title = title.encode('utf-8')
        binding = component.getUtility(IMetadataService).getMetadata(self)
        binding.setValues('silva-content', {'maintitle': title}, reindex=1)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title')
    def get_title(self):
        """Get the title of the silva object.
        """
        return component.getUtility(IMetadataService).getMetadataValue(
            self, 'silva-content', 'maintitle')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get the title of the silva object.
        """
        service = component.getUtility(IMetadataService)
        title = service.getMetadataValue(
            self, 'silva-content', 'shorttitle')
        if not title.strip():
            title = service.getMetadataValue(
                self, 'silva-content', 'maintitle')
        if not title.strip():
            title = self.get_silva_object().id
        return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_or_id')
    def get_title_or_id(self):
        """Get title or id if not available.
        """
        title = self.get_title()
        if not title.strip():
            title = self.get_silva_object().id
        return title


InitializeClass(TitledObject)


class SilvaObject(TitledObject, Security):
    """Inherited by all Silva objects.
    """
    security = ClassSecurityInfo()

    def __init__(self, id):
        TitledObject.__init__(self, id)
        self._v_creation_datetime = DateTime()

    # Use regular Zope 3 absoluteURL lookup instead of Zope 2 one.
    def absolute_url(self, relative=None):
        return absoluteURL(self, self.REQUEST)

    # MANIPULATORS

    def _set_creation_datetime(self):
        timings = {}
        ctime = getattr(self, '_v_creation_datetime', None)
        if ctime is None:
            return
        try:
            service_metadata = component.getUtility(IMetadataService)
            binding = service_metadata.getMetadata(self)
        except BindingError:
            # Non metadata object, don't do anything
            return
        if binding is None:
            return
        for elem in ('creationtime', 'modificationtime'):
            old = binding.get('silva-extra', element_id=elem)
            if old is None:
                timings[elem] = ctime
        binding.setValues('silva-extra', timings)

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_silva_object')
    def get_silva_object(self):
        """Get the object. Can be used with acquisition to get the Silva
        Document for a Version object.
        """
        return self.aq_inner

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_editable')
    def get_title_editable(self):
        """Get the title of the editable version if possible.
        """
        return self.get_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_editable')
    def get_short_title_editable(self):
        """Get the short title of the editable version if possible.
        """
        return self.get_short_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_or_id_editable')
    def get_title_or_id_editable(self):
        """Get the title of the editable version if possible, or id if
        not available.
        """
        return self.get_title_or_id()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """Check to see if the title can be set
        """
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_creation_datetime')
    def get_creation_datetime(self):
        """Return creation datetime."""
        version = self.get_previewable()
        return  component.getUtility(IMetadataService).getMetadataValue(
            version, 'silva-extra', 'creationtime')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_modification_datetime')
    def get_modification_datetime(self):
        """Return modification datetime."""
        version = self.get_previewable()
        return  component.getUtility(IMetadataService).getMetadataValue(
            version, 'silva-extra', 'modificationtime')

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_editable')
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        return self

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_previewable')
    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        return self

    security.declareProtected(SilvaPermissions.View, 'get_viewable')
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        return self


    security.declareProtected(SilvaPermissions.ReadSilvaContent, 'preview')
    def preview(self):
        """Render this as preview with the public view.

        If this is no previewable, should return something indicating this.
        """
        # XXX Should be a view
        # XXX Only keep for compatibility
        if not IPreviewLayer.providedBy(self.REQUEST):
            alsoProvides(self.REQUEST, IPreviewLayer)
        return aq_inner(self).view_version()

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'public_preview')
    def public_preview(self):
        """Public preview.

        By default this does the same as preview, but can be overridden.
        """

        # Be sure that nothing is cached by the browser.

        REQUEST = self.REQUEST

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


        return self.preview()

    security.declareProtected(SilvaPermissions.View, 'view')
    def view(self):
        """Render this with the public view. If there is no viewable,
        should return something indicating this.
        """
        return aq_inner(self).view_version()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'view_version')
    def view_version(self, version=None):
        # XXX Should be a view.
        request = self.REQUEST
        if IPreviewLayer.providedBy(self.REQUEST):
            manager = getSecurityManager()
            if not manager.checkPermission(
                SilvaPermissions.ReadSilvaContent, self):
                raise Unauthorized()
            preview_name = request.other.get('SILVA_PREVIEW_NAME', None)
            if version is None:
                if (preview_name is not None and
                    hasattr(aq_base(self), preview_name)):
                    version = getattr(self, preview_name)
                else:
                    version = self.get_previewable()
        if version is None:
            version = self.get_viewable()

        # No version
        if version is None:
            msg = _('Sorry, this ${meta_type} is not viewable.',
                    mapping={'meta_type': self.meta_type})
            return '<p>%s</p>' % translate(msg, context=request)

        # Search for a five view
        view = component.getMultiAdapter(
            (self, request), name=u'content.html')
        return view()


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_default')
    def is_default(self):
        """returns True if the SilvaObject is a default document

            by default return False, overridden on Content where an actual
            check is done
        """
        return False

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
        'is_deletable')
    def is_deletable(self):
        """always deletable"""
        return 1


InitializeClass(SilvaObject)


@grok.subscribe(ISilvaObject, IObjectCreatedEvent)
@grok.subscribe(ISilvaObject, IObjectClonedEvent)
def content_created(content, event):
    if (content != event.object or
        IObjectCopiedEvent.providedBy(event) or
        IVersionedContent.providedBy(content) or
        IRoot.providedBy(content)):
        return

    content._set_creation_datetime()


@grok.subscribe(ISilvaObject, IObjectCreatedEvent)
@grok.subscribe(ISilvaObject, IObjectClonedEvent)
@grok.subscribe(ISilvaObject, IObjectModifiedEvent)
def update_content_author_info(content, event):
    """A content have been created of modifed. Update its author
    information.
    """
    # ObjectCopiedEvent should not be ignored but content is not in
    # Zope tree when it is triggered, so metadata service doesn't
    # work. We use IObjectClonedEvent instead.
    if IObjectCopiedEvent.providedBy(event):
        return
    # In the same way, we discard event on versioned content if they
    # are about adding or removing a version.
    # XXX Modify versioning code not to have _index_version but
    # let it handle by this here.
    if (IVersionedContent.providedBy(content) and
        IContainerModifiedEvent.providedBy(event)):
        return
    if IRoot.providedBy(content):
        # If we are on the root we swallow errors, as root might not
        # be fully installed, this might not work.
        try:
            content.sec_update_last_author_info()
        except:
            pass
    else:
        content.sec_update_last_author_info()
        ICataloging(content).index()


@grok.subscribe(ISilvaObject, IObjectMovedEvent)
def index_moved_content(content, event):
    """We index all added content (due to a move).
    """
    if (not IObjectAddedEvent.providedBy(event) and
        not IObjectRemovedEvent.providedBy(event)):
        ICataloging(content).index()


@grok.subscribe(ISilvaObject, IObjectWillBeMovedEvent)
def unindex_removed_content(content, event):
    """We unindex all content that is going to be moved, and/or
    deleted.
    """
    if not IObjectWillBeAddedEvent.providedBy(event):
        ICataloging(content).unindex()
