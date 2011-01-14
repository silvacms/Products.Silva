# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import aq_parent

from five import grok
from infrae import rest
from silva.core import interfaces
from silva.core.views.interfaces import IVirtualSite
from zope.interface.interfaces import IInterface
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL

from Products.Silva.icon import registry as icons
from Products.SilvaMetadata.interfaces import IMetadataService


class ItemDetails(object):

    def __init__(self, context, query):
        self.context = context
        self.request = query.request
        self._query = query
        self._metadata = self._query.metadata.getMetadata(self.context)

    def get_title(self):
        return self.context.get_title_or_id()

    def get_description(self):
        return self._metadata.get('silva-extra', 'content_description')

    def get_modification(self):
        return self._metadata.get('silva-extra', 'modificationtime')

    def get_author(self):
        return self._metadata.get('silva-extra', 'lastauthor')

    def get_url(self):
        return absoluteURL(self.context, self.request)

    def get_path(self):
        return '/'.join(self.context.getPhysicalPath())[self._query.root_path_len:]

    def get_intid(self):
        return self._query.intid.register(self.context)

    def is_folderish(self):
        return interfaces.IContainer.providedBy(self.context)

    def get_icon(self):
        try:
            return '/'.join((self._query.root_url, icons.getIcon(self.context)))
        except ValueError:
            return '/'.join((self._query.root_url, 'globals/silvageneric.gif'))

    PROVIDERS = {
        'title': get_title,
        'intid': get_intid,
        'path': get_path,
        'description': get_description,
        'modified': get_modification,
        'author': get_author,
        'folderish': is_folderish,
        'url': get_url,
        'icon': get_icon}

    FORMATS = {
        'reference_listing': [
            'intid', 'url', 'path', 'icon', 'folderish', 'title'],
        'reference_listing_description': [
            'intid', 'url', 'path', 'icon', 'folderish', 'title', 'description'],
        'folder_listing': [
            'title', 'modified', 'author', 'folderish']
        }

    def __call__(self, name):
        return dict((key, self.PROVIDERS[key](self)) for key in self.FORMATS[name])



class Items(rest.REST):
    """Return information about an item.
    """
    grok.context(interfaces.ISilvaObject)
    grok.require('silva.ReadSilvaContent')
    grok.name('items')

    def __init__(self, context, request):
        super(Items, self).__init__(context, request)
        site = IVirtualSite(request)
        self.root = site.get_root()
        self.root_path = '/'.join(self.root.getPhysicalPath())
        self.root_path_len = len(self.root_path)
        self.root_url = absoluteURL(self.root, self.request)
        self.intid = getUtility(IIntIds)
        self.metadata = getUtility(IMetadataService)

    def get_item_details(self, format, content, content_id=None, require=None):
        if content_id is None:
            content_id = content.getId()
        info = {
            'id': content_id,
            'type': content.meta_type}
        if require is not None:
            info['implements'] = require.providedBy(content)
        info.update(ItemDetails(content, self)(format))
        return info

    def get_context_details(self, format, require):
        details = [
            self.get_item_details(
                format, self.context, content_id='.', require=require)]
        if not interfaces.IRoot.providedBy(self.context):
            details.insert(
                0,
                self.get_item_details(
                    format,aq_parent(self.context), content_id='..', require=require))
        return details

    def GET(self, format='reference_listing', intid=None, interface=None):
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
            return self.json_response(self.get_item_details(format, content))
        require = interfaces.ISilvaObject
        if interface is not None:
            require = getUtility(IInterface, name=interface)
        return self.json_response(self.get_context_details(format, require=require))


class ContainerItems(Items):
    """Return information on items in a container.
    """
    grok.context(interfaces.IContainer)

    def get_context_details(self, format, require):
        details = super(ContainerItems, self).get_context_details(format, require)
        for provider in (self.context.get_ordered_publishables,
                         self.context.get_non_publishables):
            for content in provider():
                if (require.providedBy(content) or
                    interfaces.IContainer.providedBy(content)):
                    details.append(self.get_item_details(format, content, require=require))
        return details


class ParentItems(Items):
    """Return information on parents of an item.
    """
    grok.name('parents')

    def GET(self, format='reference_listing'):
        details = []
        content = self.context
        while content and not interfaces.IRoot.providedBy(content):
            details.append(self.get_item_details(format, content))
            content = aq_parent(content)
        # Root element
        if content:
            details.append(self.get_item_details(format, content))
        details.reverse()
        return self.json_response(details)
