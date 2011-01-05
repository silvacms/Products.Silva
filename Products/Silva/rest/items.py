# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import aq_parent

from five import grok
from infrae import rest
from silva.core import interfaces
from silva.core.views.interfaces import IVirtualSite
from zope.interface.interfaces import IInterface
from zope import component
from zope.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL

from Products.Silva.icon import registry as icons


def get_icon(content):
    try:
        return icons.getIcon(content)
    except ValueError:
        return 'globals/silvageneric.gif'


class Items(rest.REST):
    """Return information about an item.
    """
    grok.context(interfaces.ISilvaObject)
    grok.require('silva.ReadSilvaContent')
    grok.name('items')

    def __init__(self, context, request):
        super(Items, self).__init__(context, request)
        self.intid = component.getUtility(IIntIds)
        site = IVirtualSite(request)
        self.root = site.get_root()
        self.root_path = '/'.join(self.root.getPhysicalPath())
        self.root_path_len = len(self.root_path)
        self.root_url = absoluteURL(self.root, self.request)

    def get_item_details(self, content, content_id=None, require=None):
        if content_id is None:
            content_id = content.getId()
        return {
            'id': content_id,
            'type': content.meta_type,
            'intid': self.intid.register(content),
            'url': absoluteURL(content, self.request),
            'path': '/'.join(content.getPhysicalPath())[self.root_path_len:],
            'icon': '/'.join((self.root_url, get_icon(content))),
            'implements': require and require.providedBy(content) or False,
            'folderish': interfaces.IContainer.providedBy(content),
            'title': content.get_title_or_id()}

    def get_context_details(self, require):
        details = [self.get_item_details(
                self.context, content_id='.', require=require)]
        if not interfaces.IRoot.providedBy(self.context):
            details.insert(0, self.get_item_details(
                    aq_parent(self.context), content_id='..', require=require))
        return details

    def GET(self, intid=None, interface=None):
        if intid is not None:
            try:
                content = self.intid.getObject(int(intid))
            except KeyError:
                # Invalid content id
                return self.json_response({
                        'id': 'broken',
                        'type': 'Broken',
                        'intid': '0',
                        'url': '', 'path': '',
                        'icon': '/'.join(
                            (self.root_url,
                             '++resource++Products.Silva/exclamation.png')),
                        'implements': False,
                        'folderish': False,
                        'title': 'Broken'})
            return self.json_response(self.get_item_details(content))
        require = interfaces.ISilvaObject
        if interface is not None:
            require = component.getUtility(IInterface, name=interface)
        return self.json_response(self.get_context_details(require=require))


class ContainerItems(Items):
    """Return information on items in a container.
    """
    grok.context(interfaces.IContainer)

    def get_context_details(self, require):
        details = super(ContainerItems, self).get_context_details(require)
        for provider in (self.context.get_ordered_publishables,
                         self.context.get_non_publishables):
            for content in provider():
                if (require.providedBy(content) or
                    interfaces.IContainer.providedBy(content)):
                    details.append(self.get_item_details(content, require=require))
        return details


class ParentItems(Items):
    """Return information on parents of an item.
    """
    grok.name('parents')

    def GET(self):
        details = []
        content = self.context
        while content and not interfaces.IRoot.providedBy(content):
            details.append(self.get_item_details(content))
            content = aq_parent(content)
        # Root element
        if content:
            details.append(self.get_item_details(content))
        details.reverse()
        return self.json_response(details)


class Addables(rest.REST):
    """ Return addables in folder
    """
    grok.context(interfaces.IContainer)
    grok.name('addables')

    def GET(self):
        meta_types = self.context.get_silva_addables_allowed_in_container()
        return self.json_response(meta_types)

