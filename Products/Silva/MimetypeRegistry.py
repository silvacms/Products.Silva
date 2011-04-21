# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.services.interfaces import IExtensionService
from silva.core.interfaces import IContentMimetypeRegistry
from zope.interface import implements
from zope.component import getUtility


class ContentMimetypeRegistry(object):
    implements(IContentMimetypeRegistry)

    def __init__(self):
        self._mimetype_to_factory = {}

    def get(self, mimetype, default=None):
        factory, extension = self._mimetype_to_factory.get(
            mimetype, (None, None))
        if factory is not None:
            # Check to see if the extension is actually installed
            service = getUtility(IExtensionService)
            if service.is_installed(extension):
                return factory
        return default

    def register(self, mimetype, factory, extension):
        self._mimetype_to_factory[mimetype] = (factory, extension)

    def unregister(self, factory):
        mimetypes = []
        for mimetype, spec in self._mimetype_to_factory.items():
            currentfactory, extensionname = spec
            if factory is currentfactory:
                mimetypes.append(mimetype)
        for mimetype in mimetypes:
            del self._mimetype_to_factory[mimetype]


mimetypeRegistry = ContentMimetypeRegistry()
