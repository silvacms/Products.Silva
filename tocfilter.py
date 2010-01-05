# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from OFS.SimpleItem import SimpleItem
from zope import interface

from silva.core.interfaces import IInvisibleService, ISilvaObject

_filters = []


def registerTocFilter(filter):
    # filter should be a callable accepting one argument that returns True
    # if the argument should be filtered out, False if it should not be
    # filtered out.
    _filters.append(filter)


def hideFromTOC(context):
    # if document is not publish, it's hidden.
    if not ISilvaObject.providedBy(context):
        return True
    viewable = context.get_viewable()
    return (viewable is None) or \
        (context.service_metadata.getMetadataValue(
            viewable, 'silva-extra', 'hide_from_tocs') == 'hide')


_filters.append(hideFromTOC)


class TOCFilterService(SimpleItem):
    interface.implements(IInvisibleService)
    meta_type = 'Silva TOC Filter Service'

    def __init__(self):
        self.id = 'service_toc_filter'
        self._title = self.meta_type

    def filter(self, context):
        for filter in _filters:
            if filter(context):
                return True
        return False
