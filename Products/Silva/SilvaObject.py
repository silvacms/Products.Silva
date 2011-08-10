# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import warnings

# Zope 3
from five import grok
from zope import component
from zope.container.interfaces import IContainerModifiedEvent
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.publisher.browser import applySkin
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IBrowserView
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
from Products.Silva.ViewCode import ViewCode
from Products.Silva.utility import interfaces as utility_interfaces
from Products.Silva.transform.interfaces import IRenderable
from Products.SilvaViews.ViewRegistry import ViewAttribute
from Products.Silva.errors import NotViewable

# Silva adapters
from Products.Silva.adapters.virtualhosting import getVirtualHostingAdapter
from Products.SilvaMetadata.Exceptions import BindingError
from Products.SilvaMetadata.interfaces import IMetadataService

from infrae.wsgi.errors import DefaultError
from silva.core.conf.utils import getSilvaViewFor
from silva.core.services.interfaces import ICataloging
from silva.core.views.interfaces import IPreviewLayer
from silva.translations import translate as _

from silva.core.interfaces import (
    ISilvaObject, IPublishable, IContent, IRoot, IVersionedContent, IFolder)



class NoViewError(Exception):
    """No view defined.
    """


class Zope3ViewAttribute(ViewAttribute):
    """A view attribute that tries to look up Zope 3 views for fun and
    profit.

    It will also try to look up Zope 3 views and favour them, so that
    you can define e.g. 'tab_edit' for your content type and it will
    work.
    """
    
    def getId(self):
        return self._view_type

    def __getitem__(self, name):
        """Lookup an adapter before to ask the view machinery.
        """
        context = self.aq_parent
        request = self.REQUEST
        # All SMI views end up including SilvaViews templates, that
        # expect to have request['model']
        request['model'] = context

        root = context.get_root()
        smi_skin = component.getUtility(Interface, root._smi_skin)

        applySkin(request, smi_skin)
        view = component.queryMultiAdapter((context, request), name=name)
        if view:
            #the view's parent is now the container, which is incorrect.
            #  the view actually needs to have this viewattribute as 
            #  the parent, so do a reparent here to fix this situation
            view.__parent__ = self
            return view
        else:
            # Default behaviour of ViewAttribute, but look at a Five
            # views if the asked one doesn't exists.
            view = getSilvaViewFor(self, self._view_type, context)
            return getattr(view, name)


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
        SilvaPermissions.AccessContentsInformation, 'get_nav_title')
    def get_nav_title(self):
        """Get the nav title of the silva object.
        """
        gmv = self.service_metadata.getMetadataValue
        title = gmv(self, 'silva-content', 'navtitle')
        if not title:
            title = gmv(self, 'silva-content', 'shorttitle')
        if not title:
            title = gmv(self, 'silva-content', 'maintitle')
        if not title:
            title = self.id
        return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_or_id')
    def get_title_or_id(self):
        """Get title or id if not available.
        """
        title = self.get_title()
        if not (title and title.strip()):
            title = self.get_silva_object().id
        return title


InitializeClass(TitledObject)


class SilvaObject(TitledObject, Security, ViewCode):
    """Inherited by all Silva objects.
    """
    security = ClassSecurityInfo()

    # allow edit view on this object
    edit = Zope3ViewAttribute('edit', 'tab_edit')

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'edit')

    # allow public view on this object
    public = ViewAttribute('public', 'render')

    def __init__(self, id):
        TitledObject.__init__(self, id)
        self._v_creation_datetime = DateTime()

    # Use regular Zope 3 absoluteURL lookup instead of Zope 2 one.
    def absolute_url(self, relative=None):
        return absoluteURL(self, self.REQUEST)

    # Query for an error page. We redefine it to have a correct object
    # as context, and not an interface ... which does not make code
    # really reusable.
    def standard_error_message(self, **kwargs):
        request = self.REQUEST
        error = kwargs.get('error_value', None)
        if error:
            context = DefaultError(error).__of__(self)
            page = component.queryMultiAdapter(
                (context, request), Interface, name='error.html')
            if page is not None:
                return page()
        if hasattr(self, 'default_standard_error_message'):
            # Fallback on ZMI views if available
            return self.default_standard_error_message(**kwargs)
        # Last resort
        return '<html><body>An error happened.</body></html>'

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


    security.declarePrivate('titleMutationTrigger')
    def titleMutationTrigger(self):
        """This trigger is called upon save of Silva Metadata. More
        specifically, when the silva-content - defining titles - set is
        being editted for this object.
        """
        if self.getId() == 'index':
            container = self.get_container()
            container._invalidate_sidebar(container)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_renderer_name')
    def set_renderer_name(self, renderer_name):
        """Set the name of the renderer selected for object.
        """
        if renderer_name == '(Default)':
            renderer_name = None
        self.get_editable()._renderer_name = renderer_name


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
        SilvaPermissions.AccessContentsInformation, 'get_short_title_editable')
    def get_short_title_editable(self):
        """Get the short title of the editable version if possible.
        """
        return self.get_short_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_nav_title_editable')
    def get_nav_title_editable(self):
        """Get the nav title of the editable version if possible.
        """
        return self.get_nav_title()

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
    def get_modification_datetime(self, update_status=1):
        """Return modification datetime."""
        version = self.get_previewable()
        return  component.getUtility(IMetadataService).getMetadataValue(
            version, 'silva-extra', 'modificationtime')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_breadcrumbs')
    def get_breadcrumbs(self, ignore_index=1):
        """Get information used to display breadcrumbs. This is a
        list of items from the Silva Root or the object being the root of
        the virtual host - which ever comes first.
        """
        warnings.warn('get_breadcrumbs() will be removed in Silva 2.4. '
                      'Please use @@absolute_url/breadcrumbs instead.',
                      DeprecationWarning, stacklevel=2)
        adapter = getVirtualHostingAdapter(self)
        root = adapter.getVirtualRoot()
        if root is None:
            root = self.get_root()

        result = []
        item = self
        while ISilvaObject.providedBy(item):
            if ignore_index: # Should the index be included?
                if not (IContent.providedBy(item) and item.is_default()):
                    result.append(item)
            else:
                result.append(item)

            if item == root: # XXX does equality always work in Zope?
                break
            item = item.aq_parent
            #if using Legacy layout, eventually an items parent will be the
            #view class.  This needs to be skipped over.  I'm not sure
            #which is the "correct" interface (IBrowserView or IBrowserPage),
            #but they both seem to work.
            if IBrowserView.providedBy(item) or IBrowserPage.providedBy(item):
                item = item.aq_parent.aq_parent
        result.reverse()
        return result

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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_renderer_name')
    def get_renderer_name(self):
        """Get the name of the renderer selected for object.

        Returns None if default is used.
        """
        return getattr(self, '_renderer_name', None)

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
        view_type = 'public'
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
            view_type = 'preview'
        if version is None:
            version = self.get_viewable()

        # No version
        if version is None:
            raise NotViewable(self)

        # Search for an XSLT renderer
        result = IRenderable(version).view(request)
        if result is not None:
            return result

        request.model = version
        request.other['model'] = version

        # Search for a five view
        view = component.queryMultiAdapter(
            (self, request), name=u'content.html')
        if not (view is None):
            return view()

        # Fallback on a Silva view
        try:
            view = self.service_view_registry.get_view(
                view_type, version.meta_type)
        except KeyError:
            msg = 'no %s view defined' % view_type
            raise NoViewError, msg
        else:
            rendered = view.render()
            try:
                del request.model
            except AttributeError:
                pass
            return rendered

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_default')
    def is_default(self):
        """returns True if the SilvaObject is a default document

            by default return False, overridden on Content where an actual
            check is done
        """
        return False

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'export_content')
    def export_content(self, export_format,
                       with_sub_publications=0,
                       last_version=0):
        """Export content using the exporter export_format.
        """
        from Products.Silva.silvaxml import xmlexport
        settings = xmlexport.ExportSettings()
        settings.setWithSubPublications(with_sub_publications)
        settings.setLastVersion(last_version)

        utility = component.getUtility(utility_interfaces.IExportUtility)
        exporter = utility.createContentExporter(self, export_format)
        return exporter.export(settings)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'export_content_format')
    def export_content_format(self, ref=None):
        """Retrieve a list of export format.
        """
        context = self
        if ref:
            context =  self.resolve_ref(ref)
        utility = component.getUtility(utility_interfaces.IExportUtility)
        return utility.listContentExporter(context)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
        'is_deletable')
    def is_deletable(self):
        """always deletable"""
        return 1


InitializeClass(SilvaObject)


@grok.subscribe(ISilvaObject, IObjectMovedEvent)
def content_moved(content, event):
    if (content != event.object or
        IObjectRemovedEvent.providedBy(event) or
        IRoot.providedBy(content)):
        return
    newParent = event.newParent

    if (IPublishable.providedBy(content) and not (
        IContent.providedBy(content) and content.is_default())):
        newParent._add_ordered_id(content)

    if event.newName == 'index':
        newParent._invalidate_sidebar(newParent)
    if not IVersionedContent.providedBy(content):
        content._set_creation_datetime()


@grok.subscribe(ISilvaObject, IObjectWillBeMovedEvent)
def content_will_be_moved(content, event):
    if (content != event.object or
        IObjectWillBeAddedEvent.providedBy(event) or
        IRoot.providedBy(content)):
        return
    container = event.oldParent
    if (IPublishable.providedBy(content) and not (
        IContent.providedBy(content) and content.is_default())):
        container._remove_ordered_id(content)
    if IFolder.providedBy(content):
        container._invalidate_sidebar(content)
    if event.oldName == 'index':
        container._invalidate_sidebar(container)


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
    if IVersionedContent.providedBy(content) and IContainerModifiedEvent.providedBy(event):
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
        # Index newly added content.
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
