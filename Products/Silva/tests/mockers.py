# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva import roleinfo

from silva.core import conf as silvaconf


class MockupVersion(Version):
    meta_type='Mockup Version'


class MockupVersionedContent(VersionedContent):
    meta_type='Mockup VersionedContent'
    silvaconf.version_class(MockupVersion)

    def __init__(self, *args):
        super(MockupVersionedContent, self).__init__(*args)

    def get_mockup_version(self, version_id):
        return self._getOb(str(version_id))


def install_mockers(root):
    root.manage_permission('Add Mockup Versions', roleinfo.AUTHOR_ROLES)
    root.service_metadata.addTypesMapping(
        ['Mockup Version'], ('silva-content', 'silva-extra',))
