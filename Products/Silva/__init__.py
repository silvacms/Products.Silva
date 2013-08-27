# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

#### Hack of the day: don't fuck up your all DB if an interface is broken.

from OFS.Uninstalled import BrokenClass
BrokenClass.__iro__ = tuple()

#### End of hack of the day

# register this extension
from silva.core import conf as silvaconf
silvaconf.extension_name('Silva')
silvaconf.extension_title('Silva Core')
silvaconf.extension_depends([])

try:
    from Products.MaildropHost import MaildropHost
    MAILDROPHOST_AVAILABLE = True
except ImportError:
    MAILDROPHOST_AVAILABLE = False

MAILHOST_ID = 'service_mailhost'


