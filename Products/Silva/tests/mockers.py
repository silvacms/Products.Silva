# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from OFS.SimpleItem import SimpleItem

from Products.Silva.Asset import Asset
from Products.Silva.Publishable import NonPublishable
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva import roleinfo

from five import grok
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import INonPublishable, IAsset, IVersionedContent
from silva.core.interfaces.adapters import IIndexEntries
from zeam.form import silva as silvaforms


class MockupVersion(Version):
    """Test version content.

    (Note: the docstring is required for traversing to work)
    """
    meta_type = 'Mockup Version'


class IMockupVersionedContent(IVersionedContent, IIndexEntries):
    pass


class MockupVersionedContent(VersionedContent):
    """Test versioned content.

    (Note: the docstring is required for traversing to work)
    """
    meta_type = 'Mockup VersionedContent'
    grok.implements(IMockupVersionedContent)
    silvaconf.priority(-11)
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
    grok.name(u'Silva VersionedContent')


class MockupEditForm(silvaforms.SMIEditForm):
    """Add form for a Mockup VersionedContent
    """
    grok.context(MockupVersionedContent)


class MockupView(silvaviews.View):
    """View mockup a Version.
    """
    grok.context(MockupVersionedContent)

    def render(self):
        return self.content.get_title()


class IMockupNonPublishable(INonPublishable):
    pass


class MockupNonPublishable(NonPublishable, SimpleItem):
    """A mockup non-publishable.
    """
    grok.implements(IMockupNonPublishable)
    meta_type = 'Mockup Non Publishable'
    silvaconf.priority(-10)
    silvaconf.icon('tests/mockers.png')


class IMockupAsset(IAsset):
    pass


class MockupAsset(Asset, SimpleItem):
    """A mockup non-publishable.
    """
    grok.implements(IMockupAsset)
    meta_type = 'Mockup Asset'
    silvaconf.priority(-10)
    silvaconf.icon('tests/mockers.png')


def install_mockers(root):
    root.manage_permission(
        'Add Mockup Assets', roleinfo.AUTHOR_ROLES)
    root.manage_permission(
        'Add Mockup Non Publishables', roleinfo.AUTHOR_ROLES)
    root.manage_permission(
        'Add Mockup Versions', roleinfo.AUTHOR_ROLES)
    root.manage_permission(
        'Add Mockup VersionedContents', roleinfo.AUTHOR_ROLES)
    root.service_metadata.addTypesMapping(
        ['Mockup Version'], ('silva-content', 'silva-extra', 'silva-settings'))
    root.service_metadata.addTypesMapping(
        ['Mockup Non Publishable'], ('silva-content', 'silva-extra',))
    root.service_metadata.addTypesMapping(
        ['Mockup Asset'], ('silva-content', 'silva-extra',))

