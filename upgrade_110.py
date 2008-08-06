# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# silva imports
from Products.Silva.upgrade import BaseRefreshAll

#-----------------------------------------------------------------------------
# 1.0.0 to 1.1.0
#-----------------------------------------------------------------------------

VERSION='1.1'

class RefreshAll(BaseRefreshAll):
    pass

refreshAll = RefreshAll(VERSION, 'Silva Root')

