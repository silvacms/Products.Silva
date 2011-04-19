# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva import roleinfo

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews


class MockupVersion(Version):
    meta_type='Mockup Version'


class MockupVersionedContent(VersionedContent):
    meta_type='Mockup VersionedContent'
    silvaconf.priority(-10)
    silvaconf.version_class(MockupVersion)

    def __init__(self, *args):
        super(MockupVersionedContent, self).__init__(*args)

    def get_mockup_version(self, version_id):
        return self._getOb(str(version_id))


class MockupView(silvaviews.View):
    """View mockup a Version.
    """
    silvaconf.context(MockupVersion)

    def render(self):
        return self.content.get_title()


def install_mockers(root):
    root.manage_permission('Add Mockup Versions', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Add Mockup VersionedContents', roleinfo.AUTHOR_ROLES)
    root.service_metadata.addTypesMapping(
        ['Mockup Version'], ('silva-content', 'silva-extra',))

