# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from AccessControl import getSecurityManager

from zope.component import getUtility
from silva.core import conf as silvaconf
from silva.core.interfaces import IViewableObject, IContainer
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import IContentFilteringService
from silva.core.views.interfaces import IDisableNavigationTag, IPreviewLayer
from Products.SilvaMetadata.interfaces import IMetadataService


class Filter(object):
    """Appy a list of filter to a list contents.
    """

    def __init__(self, instances):
        self._instances = instances

    def filter(self, content):
        for instance in self._instances:
            if instance(content):
                return False
        return True

    def __call__(self, contents):
        return filter(self.filter, contents)


class FilteringRegistry(object):
    """Register available filters.
    """

    def __init__(self):
        self.clear()

    def register(self, factory):
        self._factories.append(factory)

    def clear(self):
        self._factories = []

    def __call__(self, request):
        instances = []
        for factory in self._factories:
            instances.append(factory(request))
        return Filter(instances)

registry = FilteringRegistry()


class ViewPermissionFilter(object):
    """Filter out elements where you don't have the view permission.
    """

    def __init__(self, request):
        self.check = getSecurityManager().checkPermission

    def __call__(self, content):
        return not self.check('View', content)

registry.register(ViewPermissionFilter)


class MarkerFilter(object):
    """Filter out elements that are explict marked with a marker.
    """

    def __init__(self, request):
        pass

    def __call__(self, content):
        return IDisableNavigationTag.providedBy(content)


registry.register(MarkerFilter)


class ViewableFilter(object):
    """Filter out elements that are not viewable, or are marked in the
    metadata set.
    """

    def __init__(self, request):
        self.get = lambda content: content.get_viewable()
        if IPreviewLayer.providedBy(request):
            self.get = lambda content: content.get_previewable()
        self.metadata = getUtility(IMetadataService).getMetadataValue

    def __call__(self, content):
        if not IViewableObject.providedBy(content):
            return True
        item = self.get(content)
        # Item is none will account for unpublished content.
        return (
            (item is None) or
            (self.metadata(item, 'silva-settings', 'hide_from_tocs') == 'hide'))

registry.register(ViewableFilter)


class ContainerFilter(object):
    """Filter out container that don't have a published index.
    """

    def __init__(self, request):
        self.get = lambda content: content.get_viewable()
        if IPreviewLayer.providedBy(request):
            self.get = lambda content: content.get_previewable()

    def __call__(self, content):
        if IContainer.providedBy(content):
            default = content.get_default()
            if default is None:
                return True
            if self.get(default) is None:
                return True
        return False

registry.register(ContainerFilter)


class FilteringService(SilvaService):
    meta_type = 'Silva Filtering Service'
    grok.implements(IContentFilteringService)
    grok.name('service_filtering')
    silvaconf.default_service()

    def filter(self, request):
        return registry(request)

    def contents(self, contents, request):
        return self.filter(request)(contents)


import zope.deferredimport
zope.deferredimport.define(
    TOCFilterService='Products.Silva.tocfilter:FilteringService')


