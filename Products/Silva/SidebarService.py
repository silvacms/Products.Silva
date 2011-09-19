# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from operator import attrgetter

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
from Products.Silva.icon import get_meta_type_icon
from Products.Silva.Folder import meta_types_for_interface

# Silva interfaces
from silva.core import conf as silvaconf
from silva.core.cache.store import Store
from silva.core.interfaces import IContainer, IPublication, IRoot
from silva.core.services.base import SilvaService
from silva.core.interfaces import (ISidebarService, IInvalidateSidebarEvent,
    ISilvaObject)
from silva.core.services.interfaces import ICataloging

ICON_TAG = '<img src="%s" width="16" height="16" border="0" '\
    'alt="%s" title="%s" />'

def render_icon(request, meta_type):
    icon = request['BASE1'] + '/' + get_meta_type_icon(meta_type)
    return  ICON_TAG % (icon, meta_type, meta_type)

def get_content_to_reindex(start, extra=None, recursive=0):
    if extra is not None:
        for content in extra:
            yield content
    if recursive:
        folder_types = meta_types_for_interface(IContainer)
        to_list = [start]
        while to_list:
            content = to_list.pop(0)
            yield content
            container_ids = set(content.objectIds(folder_types))
            for publishable_id in content._ordered_ids:
                if publishable_id in container_ids:
                    candidate = content._getOb(publishable_id)
                    if recursive > 1 or candidate.is_transparent():
                        to_list.insert(0, candidate)
    else:
        yield start


class SidebarNode(object):
    brain = None
    position = 999

    def __init__(self):
        self.children = {}

    def set_brain(self, brain):
        self.brain = brain
        self.position = brain.sidebar_position


class SidebarView(grok.View):
    grok.name('smi_sidebar')
    grok.context(IPublication)

    def get_tree(self):
        catalog = self.context.service_catalog
        raw_path = self.context.getPhysicalPath()
        ignore_len = len(raw_path)
        path = '/'.join(raw_path)

        tree = {}
        for brain in catalog(
            meta_type=meta_types_for_interface(IContainer),
            sidebar_parent=path):

            level = tree
            brain_path = brain.getPath().split('/')[ignore_len:]
            last_position = len(brain_path) - 1
            for position, part in enumerate(brain_path):
                if part not in level:
                    level[part] = SidebarNode()
                if position == last_position:
                    level[part].set_brain(brain)
                else:
                    level = level[part].children

        items = []

        def serialize(level, depth):
            level_items = level.values()
            level_items.sort(key=attrgetter('position'))
            for item in level_items:
                if item.brain is None:
                    continue
                items.append({
                        'meta_type': item.brain.meta_type,
                        'url': item.brain.getURL(),
                        'id': item.brain.id,
                        'title': item.brain.sidebar_title or 'no title',
                        'indent': depth * 10 + 4,
                        'icon': render_icon(self.request, item.brain.meta_type),
                        })
                if item.children:
                    serialize(item.children, depth + 1)

        serialize(tree, 0)
        return items


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
    def render(self, obj, tab_name, vein=None, request=None):
        """Returns the rendered PT

        Checks whether the PT is already available cached, if so
        renders the tab_name into it and returns it, if not renders
        the full pagetemplate and stores that in the cache
        """
        # vein is unused, keep for compatiblity.
        pub = obj.get_publication()
        adapter = getVirtualHostingAdapter(pub)
        if adapter.containsVirtualRoot():
            # If the virtual host points inside the publication,
            # use that point as 'publication' to start from.
            pub = adapter.getVirtualRoot()

        abs_url = pub.absolute_url()

        sidebar_cache = Store('sidebar_cache', 'shared')
        template = sidebar_cache.get(abs_url)
        if template is None:
            if request is None:
                request = self.REQUEST

            template = SidebarView(pub, request)()
            sidebar_cache[abs_url] = template

            # now add the abs_url to the path_mapping of the storage so we
            # can find it for invalidation when the invalidation is done
            # from another virtual host.
            mapping = Store('sidebar_paths', 'shared')
            ph_path = pub.getPhysicalPath()
            abs_urls = mapping.get(ph_path, tuple()) + (abs_url,)
            mapping[ph_path] = abs_urls

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

        return template

    security.declareProtected(
        SilvaPermissions.ViewAuthenticated, 'invalidate')
    def invalidate(self, obj, delete=0, extra=None, recursive=0):
        """Invalidate the cache for a specific object
        """
        # Reindex the object in order to update sidebar_ attributes in
        # the catalog.
        if not delete:
            for content in get_content_to_reindex(
                obj, extra=extra, recursive=recursive):
                ICataloging(content).index()

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
