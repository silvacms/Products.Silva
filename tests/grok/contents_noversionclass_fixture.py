# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion


class MyVersionContent(CatalogedVersion):

    meta_type = 'My Version Content'


class MyVersionedContent(CatalogedVersionedContent):

    meta_type = 'My Versioned Content'
