# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from urlparse import urlparse
import re

# Zope
from Acquisition import aq_base
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import Redirect

# Silva
from Products.Silva import icon

from silva.core.interfaces import (IContent, IContainer, IAsset,
                                   IPublishable, IGhostFolder, ISilvaObject)

strip_poss_re = re.compile('\&?possible_container=[^\&]*')
repl_sel_path_re = re.compile('(\&?selected_path=)[^\&]*')

from zope.interface import alsoProvides
from silva.core.smi.interfaces import ISMILayer

class ObjectLookup(BrowserView):
    """View that allows browsing and searching for objects.
    """
    render_lookup = ViewPageTemplateFile('object_lookup.pt')

    def __call__(self):
        
        alsoProvides(self.request, ISMILayer)
        psp = self.request.get('possible_container',None)
        if psp:
            scheme, netloc, ppath, parameters, query, fragment = urlparse(psp)
            if not (scheme or netloc) and ppath:
                #we don't need to un-vhost the path, since the path
                # is traversed to (removing the vhosting)
                obj = self.context.restrictedTraverse(ppath,None)
                if obj and ISilvaObject.providedBy(obj):
                    sel_path = None
                    if not IContainer.providedBy(obj):
                        sel_path = '/'.join(obj.getPhysicalPath())
                        obj = obj.get_container()
                    #compute absolute url, add query string, redirect
                    # if obj was originally not a container, add to
                    # query string the selected_path
                    url = obj.absolute_url() + '/@@object_lookup?'
                    qs = strip_poss_re.sub('',self.request['QUERY_STRING'])
                    if sel_path:
                        if qs.find('selected_path') > -1:
                            qs = repl_sel_path_re.sub(r'\1%s'%sel_path,qs)
                        else:
                            qs += '&selected_path=%s'%sel_path
                    if qs.find('startpath') == -1:
                        #XXX I think we only want to set startpath if it isn't
                        #    already set?
                        qs += '&startpath=%s'%'/'.join(self.context.getPhysicalPath())
                    url += qs

                    self.request.RESPONSE.redirect(url)
                    raise Redirect(url)
        return self.render_lookup()

    def renderIcon(self, obj=None, meta_type='Unknown'):
        """Gets the icon for the object and wraps that in an image tag
        """
        tag = ('<img src="%(icon_path)s" width="16" height="16" border="0" '
               'alt="%(alt)s" />')
        if obj is None:
            icon_path = ('%s/globals/silvageneric.gif' %
                         self.context.REQUEST['BASE2'])
            return tag % {'icon_path': icon_path, 'alt': meta_type}
        try:
            icon_path = '%s/%s' % (self.context.REQUEST['BASE1'],
                icon.registry.getIcon(obj))
        except ValueError:
            icon_path = getattr(aq_base(obj), 'icon', None)
            if icon_path is None:
                icon_path = ('%s/globals/silvageneric.gif' %
                             self.context.REQUEST['BASE2'])
            meta_type = getattr(obj, 'meta_type')
        return tag % {'icon_path': icon_path, 'alt': meta_type}

    def displayContainerReferenceButton(self, filter):
        """
        Returns True if, given the filter, the context should display
        the 'place reference to this container...' button.
        """
        if not filter or filter==["Container"] or filter==['']:
            return True
        #assume filter contains a list of meta types
        return (self.context.meta_type in filter)

    def objectLookupGetObjects(self, filter=None, show_add=False):
        """Returns objects to be displayed for the lookup window

            filter: 'Asset', 'Content', a certain meta_type (string) or a
                        list of meta_types

            show_add: whether or not to show the 'add' button (to add new
                        objects)

            returns a tuple with 5 values:

              default - can be None or refers to the default object (index)

              publishables - an ordered list of publishable items

              assets - a list of assets (ordered by id)

              addables - a list of meta_types that are allowed to be added
                        to the page

              visible_containers - Contains the list of containers that
                                   will only be visible (not selectable).
        """
        model = self.context

        default = None
        ordered_publishables = []
        assets = []
        addables = []
        all_addables = []

        visible_containers = []

        filter = filter or []

        if show_add and not IGhostFolder.providedBy(model):
            all_addables = model.get_silva_addables()

        if isinstance(filter, str):
            filter = filter.split("|")

        if filter == ['Asset']:
            assets = model.get_assets()
            ordered_publishables = [
                content for content in model.get_ordered_publishables()
                if IContainer.providedBy(content)]
            visible_containers = ordered_publishables
            if show_add:
                addables = [a['name'] for a in all_addables if
                            IAsset.implementedBy(a['instance'])]
        elif filter == ['Content']:
            default = model.get_default()
            ordered_publishables = []
            if default:
                ordered_publishables.append(default)
            ordered_publishables.extend(
                [content for content in model.get_ordered_publishables() if
                 IContent.providedBy(content) or IContainer.providedBy(content)]
            )
            visible_containers = [
                content for content in ordered_publishables
                if IContainer.providedBy(content)]
            if show_add:
                addables = [a['name'] for a in all_addables if
                            IContent.implementedBy(a['instance'])]
        elif filter == ['Container']:
            ordered_publishables = [
                content for content in model.get_ordered_publishables()
                if IContainer.providedBy(content)]
            if show_add:
                addables = [a['name'] for a in all_addables if
                            IContainer.implementedBy(a['instance'])]
        elif filter == ['Publishable']:
            default = model.get_default()
            ordered_publishables = []
            if default:
                ordered_publishables.append(default)
            ordered_publishables.extend(model.get_ordered_publishables())
            if show_add:
                addables = [a['name'] for a in all_addables if
                            IPublishable.implementedBy(a['instance'])]
        else:
            # get all objects using filter, then divide them the way they
            # should be returned
            if not filter or filter == ['']:
                # return everything
                default = model.get_default()
                ordered_publishables = model.get_ordered_publishables()
                assets = model.get_assets()
                if show_add:
                    addables = [a['name'] for a in all_addables]
            else:
                #assume filter contains a list of meta types
                objects = model.objectValues(filter)
                defaultobj = model.get_default()
                if defaultobj and defaultobj in objects:
                    default = defaultobj
                for content in model.get_ordered_publishables():
                    if content in objects:
                        ordered_publishables.append(content)
                    elif IContainer.providedBy(content):
                        ordered_publishables.append(content)
                        visible_containers.append(content)
                for content in model.get_assets():
                    if content in objects:
                        assets.append(content)

                if show_add:
                    addables = [
                        a['name'] for a in all_addables if a['name'] in filter]

        # sort the assets
        assets.sort(lambda a, b: cmp(a.id, b.id))

        return (default, ordered_publishables, assets, addables, visible_containers)


class SidebarView(BrowserView):
    def render(self, tab_name, vein):
        # XXX once we move everything to five views, the object_lookup
        # template can become much much simpler.
        context = self.context.aq_inner
        sidebar = context.service_sidebar.render(context, tab_name, vein)
        sidebar = sidebar.replace('/edit/', '/')
        return sidebar
