# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from five import grok
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import IContentFilteringService
from silva.core.views.interfaces import IDisableNavigationTag

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


_filters.append(IDisableNavigationTag.providedBy)
_filters.append(hideFromTOC)


class TOCFilterService(SilvaService):
    meta_type = 'Silva TOC Filter Service'
    grok.implements(IContentFilteringService)
    grok.name('service_filtering')
    silvaconf.default_service()

    def filter(self, context):
        for filter in _filters:
            if filter(context):
                return True
        return False
