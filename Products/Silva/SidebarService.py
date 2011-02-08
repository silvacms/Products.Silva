# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.adapters.virtualhosting import getVirtualHostingAdapter
from Products.Silva.helpers import add_and_edit

# Silva interfaces
from silva.core import conf as silvaconf
from silva.core.cache.store import Store
from silva.core.services.base import SilvaService
from silva.core.interfaces import (ISidebarService, IInvalidateSidebarEvent,
    ISilvaObject, IPublication, IRoot)


class SidebarService(SilvaService):
    """Service for sidebar cache"""

    meta_type = 'Silva Sidebar Service'
    title = 'Silva Sidebar Cache'

    security = ClassSecurityInfo()

    implements(ISidebarService)
    silvaconf.icon('www/sidebar_service.png')
    silvaconf.factory('manage_addSidebarServiceForm')
    silvaconf.factory('manage_addSidebarService')

    def __init__(self, id, title):
        self.id = id
        self._title = title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'render')
    def render(self, obj, tab_name, vein):
        """Returns the rendered PT

        Checks whether the PT is already available cached, if so
        renders the tab_name into it and returns it, if not renders
        the full pagetemplate and stores that in the cache
        """
        pub = obj.get_publication()
        adapter = getVirtualHostingAdapter(pub)
        if adapter.containsVirtualRoot():
            # If the virtual host points inside the publication,
            # use that point as 'publication' to start from.
            pub = adapter.getVirtualRoot()

        abs_url = pub.absolute_url()
        ph_path = pub.getPhysicalPath()

        sidebar_cache = Store('sidebar_cache', 'shared')
        cached_template = sidebar_cache.get(abs_url)
        if cached_template is None:
            cached_template = self._render_template(pub)
            sidebar_cache[abs_url] = cached_template

            # now add the abs_url to the path_mapping of the storage so we
            # can find it for invalidation when the invalidation is done
            # from another virtual host.
            mapping = Store('sidebar_paths', 'shared')
            abs_urls = mapping.get(ph_path, tuple()) + (abs_url,)
            mapping[ph_path] = abs_urls

        return self._finalize_template(
            cached_template, obj, tab_name, vein)

    security.declareProtected(
        SilvaPermissions.ViewAuthenticated, 'invalidate')
    def invalidate(self, obj):
        """Invalidate the cache for a specific object
        """
        pub = obj.get_publication()
        ph_path = pub.getPhysicalPath()
        sidebar_paths = Store('sidebar_paths', 'shared')
        abs_urls = sidebar_paths.get(ph_path)

        if abs_urls is None:
            return

        sidebar_cache = Store('sidebar_cache', 'shared')
        for url in  abs_urls:
            if url in sidebar_cache:
                del sidebar_cache[url]

        if ph_path in sidebar_paths:
            del sidebar_paths[ph_path]

    def _render_template(self, pub):
        """Actually render the pagetemplate

        Mind that some elements will be put in later on (e.g.,
        tab_name, focus class)
        """
        request = self.REQUEST
        model = request.get('model')
        request.set('model', pub)
        rendered = self.aq_inner.service_resources.Silva.sidebar_template()
        request.set('model', model)
        return rendered

    def _finalize_template(self, template, obj, tab_name, vein):
        """Add the tab_name and the focus class to the template
        """
        # XXX ugly hack: we're putting in the focus class into the
        # string by searching for the url of the current object and
        # replacing the classname in the same tag
        focused_url = obj.absolute_url()
        url_pos = template.rfind('%s/edit/{__vein_id__}' % focused_url)
        # this requires the class to ALWAYS be before the url
        class_pos = template.rfind('{__class__}', 0, url_pos)
        template = template[:class_pos] + 'selected' + template[class_pos + 11:]

        template = template.replace('{__class__}', 'unselected')
        template = template.replace('{__vein_id__}', tab_name)
        template = template.replace('{__vein__}', vein)
        template = template.replace('{__absolute_url__}', self.REQUEST.URL)

        return template

InitializeClass(SidebarService)

manage_addSidebarServiceForm = PageTemplateFile(
    "www/sidebarServiceAdd", globals(),
    __name__ = 'manage_addSidebarServiceForm')

def manage_addSidebarService(self, id, title, REQUEST=None):
    """Add the sidebar service"""
    id = self._setObject(id, SidebarService(id, title))
    add_and_edit(self, id, REQUEST)
    return ''


@grok.subscribe(ISilvaObject, IInvalidateSidebarEvent)
def invalidate_sidebar(obj, event):
    service_sidebar = obj.get_root().service_sidebar
    service_sidebar.invalidate(obj)
    if (IPublication.providedBy(obj) and
            not IRoot.providedBy(obj)):
        service_sidebar.invalidate(obj.aq_inner.aq_parent)
