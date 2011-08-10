# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


import zope.deferredimport
import silva.core.interfaces

zope.deferredimport.deprecated(
    'Please import from silva.core.interface instead, '
    'this import location will be removed in Silva 2.3.',
    **dict(map(lambda s: (s, 'silva.core.interfaces:%s' % s),
               filter(lambda s: not (s.startswith('_') or s.startswith('grok')),
                      dir(silva.core.interfaces)))))
