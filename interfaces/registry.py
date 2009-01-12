# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface


class IRegistry(interface.Interface):
    """An registry is a special utility which exists only in memory
    (it's not dump in the ZOBD).
    """


