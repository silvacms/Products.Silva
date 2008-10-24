# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five import BrowserView

class EmptyAction(BrowserView):

    def __call__(self):
        # by default, there's no additional action
        return ''
