# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from zope.component import getUtility
from zope.cachedescriptors.property import CachedProperty
from silva.core.messages.interfaces import IMessageService


NS_SILVA_URI = 'http://infrae.com/namespace/silva'
NS_SILVA_CONTENT_URI = 'http://infrae.com/namespace/metadata/silva-content'
NS_SILVA_EXTRA_URI = 'http://infrae.com/namespace/metadata/silva-extra'


logger = logging.getLogger('silva.xml')


class ImportExportMessaging(object):
    """ Mixin for reporting import / export problems.

    The class it is mixed in should define self.request
    """

    @CachedProperty
    def _messageService(self):
        return getUtility(IMessageService)

    def reportError(self, message, content=None, path=None):
        if content or path:
            if content is not None:
                path = "/".join(content.getPhysicalPath())
            message += ' at %s' % path

        logger.warn(message)
        if hasattr(self, 'request') and self.request is not None:
            self._messageService.send(message, self.request, namespace='error')
