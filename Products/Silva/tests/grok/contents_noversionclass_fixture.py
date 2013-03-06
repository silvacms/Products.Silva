# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version


class MyVersionContent(Version):
    meta_type = 'My Version Content'


class MyVersionedContent(VersionedContent):
    meta_type = 'My Versioned Content'
