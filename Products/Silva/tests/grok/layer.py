# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

  Grok this module:

    >>> grok('Products.Silva.tests.grok.layer')

  Now we have a new layer:

    >>> from silva.core.layout.helpers import getAvailableSkins
    >>> 'My test skin' in getAvailableSkins()
    True

"""

from silva.core.layout.interfaces import ISilvaLayer, ISilvaSkin
from silva.core import conf as silvaconf


class IMyTestLayer(ISilvaLayer):
    """My test layer.
    """


class ISilvaSkin(IMyTestLayer, ISilvaSkin):
    """My test skin.
    """

    silvaconf.skin('My test skin')

