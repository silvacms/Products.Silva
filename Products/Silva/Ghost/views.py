# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zope.component import queryMultiAdapter

# Zope 2
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

# Silva
from silva.core.interfaces import IGhost
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IView
from silva.translations import translate as _


class GhostView(silvaviews.View):
    grok.context(IGhost)

    broken_message = _(u"This content is unavailable. "
                       u"Please inform the site manager.")

    def render(self):
        haunted = self.content.get_haunted()
        if haunted is None:
            return self.broken_message
        permission = self.is_preview and 'Read Silva content' or 'View'
        if not getSecurityManager().checkPermission(permission, haunted):
            raise Unauthorized(
                u"You do not have permission to "
                u"see the target of this ghost")
        view = queryMultiAdapter((haunted, self.request), name="content.html")
        if view is None:
            return self.broken_message
        if IView.providedBy(view) and view.content is None:
            return self.broken_message
        return view()

