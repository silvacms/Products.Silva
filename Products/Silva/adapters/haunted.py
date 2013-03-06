# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core import interfaces
from silva.core.references.interfaces import IReferenceService
from zope.component import getUtility


class Haunted(grok.Adapter):
    """Adapted content for retrieving the 'iterator' of haunting
    objects (Ghosts).
    """
    grok.implements(interfaces.IHaunted)
    grok.context(interfaces.IContent)

    def getHaunting(self):
        service = getUtility(IReferenceService)
        for reference in service.get_references_to(
            self.context, name=u'haunted'):
            yield reference.source.get_silva_object()


class HauntedGhost(Haunted):
    """Adapted content for retrieving the 'iterator' of haunting
    objects (Ghosts).
    """
    grok.context(interfaces.IGhost)

    def getHaunting(self):
        # Nothing to look for - Ghost cannot be haunted. Don't yield anything
        # XXX how to not yield anything??
        if None:
            yield None

