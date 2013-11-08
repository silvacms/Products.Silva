# -*- coding: utf-8 -*-
# Copyright (c) 2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.interfaces import IGhostFolder, IAddableContents


class AddableContents(grok.Adapter):
    grok.context(IGhostFolder)
    grok.implements(IAddableContents)
    grok.provides(IAddableContents)

    def get_authorized_addables(self):
        return []

    def get_container_addables(self):
        return []

    def get_all_addables(self):
        return []



