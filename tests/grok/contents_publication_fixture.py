# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from Products.Silva.Publication import Publication


class MyPublication(Publication):

    meta_type = 'My Publication'


