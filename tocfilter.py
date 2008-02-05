# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt

from OFS.SimpleItem import SimpleItem

_filters = []

def registerTocFilter(filter):
    # filter should be a callable accepting one argument that returns True
    # if the argument should be filtered out, False if it should not be
    # filtered out.
    _filters.append(filter) 
        
def hideFromTOC(context):
    viewable = context.get_viewable()
    return context.service_metadata.getMetadataValue(
        viewable, 'silva-extra', 'hide_from_tocs') == 'hide'

_filters.append(hideFromTOC)
        
class TOCFilterService(SimpleItem):
    
    meta_type = 'Silva TOC Filter Service'

    def __init__(self):
        self.id = 'service_toc_filter'
        self._title = self.meta_type
    
    def filter(self, context):
        for filter in _filters:
            if filter(context):
                return True
        return False
