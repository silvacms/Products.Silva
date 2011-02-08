# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zExceptions import BadRequest

from five import grok
from infrae import rest
from silva.core import interfaces


class ImageResize(rest.REST):
    """Return information about an item.
    """
    grok.context(interfaces.IImage)
    grok.require('silva.ChangeSilvaContent')
    grok.name('image.resize')

    def POST(self, width, height):
        try:
            width = int(width)
            height = int(height)
        except:
            raise BadRequest(u"width or height are not integers")

        if width < 1:
            width = 1
        if height < 1:
            height = 1
        self.context.set_web_presentation_properties(
            self.context.getWebFormat(),
            "%sx%s" % (width, height),
            self.context.getWebCrop())
        return self.json_response({"status": "success"})

