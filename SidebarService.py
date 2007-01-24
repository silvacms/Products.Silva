# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: SidebarService.py,v 1.23 2006/01/24 16:14:12 faassen Exp $
# Zope
from zope.interface import implements

from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
from SidebarCache import SidebarCache
import SilvaPermissions
from helpers import add_and_edit
# Silva adapters
from Products.Silva.adapters.virtualhosting import getVirtualHostingAdapter
# Silva interfaces
from interfaces import ISidebarService

class SidebarService(SimpleItem):
    """Service for sidebar cache"""

    meta_type = 'Silva Sidebar Service'
    title = 'Silva Sidebar Cache'
    
    security = ClassSecurityInfo()

    implements(ISidebarService)
    
    cache_container_id = 'temp_folder'

    manage_options = (
        {'label':'Edit', 'action':'manage_sidebarServiceEditTab'},
        ) + SimpleItem.manage_options

    security.declareProtected(
        'View management screens', 'manage_sidebarServiceEditTab')
    manage_sidebarServiceEditTab = PageTemplateFile(
        'www/sidebarServiceEditTab', globals(), 
        __name__='manage_sidebarServiceEditTab')

    def __init__(self, id, title):
        self.id = id
        self._title = title

    security.declareProtected(
        'View management screens', 'manage_sidebarServiceEdit')
    def manage_sidebarServiceEdit(self, id):
        """set the cache container
        """
        # check validity
        if getattr(self.aq_inner, id, None) is None:
            # not valid
            msg = 'Id does not provide for an existing cache container'
        else:
            self.cache_container_id = id
            msg = 'Id changed'

        return self.manage_sidebarServiceEditTab(manage_tabs_message=msg)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render')
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

        storage = self._get_storage()
        sidebar_cache = storage._sidebar_cache

        cached_template = sidebar_cache.get(abs_url)
        
        if cached_template is None:
            cached_template = sidebar_cache[abs_url] = self._render_template(pub)
            # now add the abs_url to the path_mapping of the storage so we
            # can find it for invalidation when the invalidation is done
            # from another virtual host.
            mapping = storage._path_mapping
            if not mapping.has_key(ph_path):
                mapping[ph_path] = ()
            abs_urls = mapping[ph_path] + (abs_url,)
            mapping[ph_path] = abs_urls

        return self._finalize_template(
            cached_template, obj, tab_name, vein)

    security.declareProtected(SilvaPermissions.ViewAuthenticated,
                              'invalidate')
    def invalidate(self, obj):
        """Invalidate the cache for a specific object
        """
        storage = self._get_storage(create=0)
        if storage is None:
            return
            
        pub = obj.get_publication()
        ph_path = pub.getPhysicalPath()
        abs_urls = storage._path_mapping.get(ph_path)

        if abs_urls is None:
            return
        for abs_url in abs_urls:
            del storage._sidebar_cache[abs_url]
        del storage._path_mapping[ph_path]

    def _get_storage(self, create=1):
        cc = getattr(self.aq_inner, self.cache_container_id)
        storage = getattr(cc, 'silva_sidebar_cache', None)
        if storage is None and create:
            cc.silva_sidebar_cache = SidebarCache('silva_sidebar_cache')
            # Trigger persistence machinery
            cc._p_changed = 1
            storage = cc.silva_sidebar_cache
        return storage
    
    def _render_template(self, pub):
        """Actually render the pagetemplate

        Mind that some elements will be put in later on (e.g., tab_name, focus class)
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
        # XXX ugly hack: we're putting in the focus class into the string by searching
        # for the url of the current object and replacing the classname in the same
        # tag
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
