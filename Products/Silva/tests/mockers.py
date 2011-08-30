# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva import roleinfo

from five import grok
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces.adapters import IIndexEntries
from zeam.form import silva as silvaforms


class MockupVersion(Version):
    meta_type = 'Mockup Version'


class MockupVersionedContent(VersionedContent):
    meta_type = 'Mockup VersionedContent'
    grok.implements(IIndexEntries)
    silvaconf.priority(-10)
    silvaconf.version_class(MockupVersion)
    silvaconf.icon('tests/mockers.png')

    def __init__(self, *args):
        super(MockupVersionedContent, self).__init__(*args)
        self.__entries = []

    def set_entries(self, entries):
        self.__entries = entries

    def get_entries(self):
        return list(self.__entries)

    def get_mockup_version(self, version_id):
        return self._getOb(str(version_id))


class MockupAddForm(silvaforms.SMIAddForm):
    """Add form for a Mockup VersionedContent
    """
    grok.context(MockupVersionedContent)
    grok.name(u'Silva Link')


class MockupEditForm(silvaforms.SMIEditForm):
    """Add form for a Mockup VersionedContent
    """
    grok.context(MockupVersionedContent)


class MockupView(silvaviews.View):
    """View mockup a Version.
    """
    silvaconf.context(MockupVersionedContent)

    def render(self):
        return self.content.get_title()


def install_mockers(root):
    root.manage_permission('Add Mockup Versions', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Add Mockup VersionedContents', roleinfo.AUTHOR_ROLES)
    root.service_metadata.addTypesMapping(
        ['Mockup Version'], ('silva-content', 'silva-extra',))

