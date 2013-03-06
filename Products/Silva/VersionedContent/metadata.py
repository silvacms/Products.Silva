# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from Products.SilvaMetadata.Binding import DefaultMetadataBindingFactory
from silva.core.interfaces import IVersionedObject


class VersionedMetadataBindingFactory(DefaultMetadataBindingFactory):
    grok.context(IVersionedObject)
    read_only = True

    def get_content(self):
        # Return read-only metadata of the published, or next or closed version.
        version_id = self.context.get_public_version()
        if version_id is None:
            version_id = self.context.get_next_version()
            if version_id is None:
                version_id = self.context.get_last_closed_version()
                if version_id is None:
                    return None
        return self.context._getOb(version_id, None)
