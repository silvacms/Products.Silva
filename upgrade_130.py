# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# silva imports
from Products.Silva.upgrade import BaseRefreshAll

#-----------------------------------------------------------------------------
# 1.2.0 to 1.3.0
#-----------------------------------------------------------------------------

VERSION='1.3'

class RefreshAll(BaseRefreshAll):
    pass

refreshAll = RefreshAll(VERSION, 'Silva Root')

