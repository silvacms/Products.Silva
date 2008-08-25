# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

  >>> five.grok.testing.grok(__name__)

  Now we have a new layer:
 
  >>> from Products.SilvaLayout.helpers import getAvailableSkins
  >>> 'My test skin' in getAvailableSkins()
  True

"""

import five.grok.testing

from silva.core.layout.interfaces import ISilvaLayer, ISilvaSkin
from silva.core import conf as silvaconf

class IMyTestLayer(ISilvaLayer):
    """My test layer.
    """


class ISilvaSkin(IMyTestLayer, ISilvaSkin):
    """My test skin.
    """

    silvaconf.skin('My test skin')

