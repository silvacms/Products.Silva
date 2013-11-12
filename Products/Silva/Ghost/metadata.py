# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok

from Products.SilvaMetadata.Binding import DefaultMetadataBindingFactory

from silva.core.interfaces import IGhostAware
from silva.core.views.interfaces import IPreviewLayer


class GhostMetadataBindingFactory(DefaultMetadataBindingFactory):
    grok.context(IGhostAware)
    read_only = True

    def get_content(self):
        haunted = self.context.get_haunted()
        if haunted is not None:
            if IPreviewLayer.providedBy(haunted.REQUEST):
                return haunted.get_previewable()
            return haunted.get_viewable()
        return None

