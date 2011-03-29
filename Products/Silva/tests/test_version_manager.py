# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from DateTime import DateTime

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IVersionManager, VersioningError
from zope.interface.verify import verifyObject


class MockupVersion(Version):
    meta_type='MockupVersion'


class MockupVersionedContent(VersionedContent):
    meta_type='MockupVersionedContent'

    def __init__(self, *args):
        super(MockupVersionedContent, self).__init__(*args)
        self.create_mockup_version('0')

    def create_mockup_version(self, version_id):
        self._setObject(str(version_id), MockupVersion(str(version_id)))
        self.create_version(str(version_id), None, None)


class VersionManagerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        self.root._setObject('content', MockupVersionedContent('content'))

        for version_id in range(1, 5):
            IPublicationWorkflow(self.root.content).publish()
            self.root.content.create_mockup_version(str(version_id))

    def test_implementation(self):
        published = self.root.content.get_viewable()
        manager = IVersionManager(published)
        self.assertTrue(verifyObject(IVersionManager, manager))

    def test_get_publication_datetime(self):
        """Verify get_publication_datetime
        """
        manager = IVersionManager(self.root.content.get_editable())
        self.assertEqual(manager.get_publication_datetime(), None)

        now = DateTime()
        self.root.content.set_unapproved_version_publication_datetime(now)
        self.assertEqual(manager.get_publication_datetime(), now)

    def test_get_expiration_datetime(self):
        """Verify get_expiration_datetime
        """
        manager = IVersionManager(self.root.content.get_editable())
        self.assertEqual(manager.get_expiration_datetime(), None)

        now = DateTime()
        self.root.content.set_unapproved_version_expiration_datetime(now)
        self.assertEqual(manager.get_expiration_datetime(), now)

    def test_delete_unapproved_version(self):
        """Delete an unapproved version.
        """
        self.assertEqual(len(self.root.content.objectIds('MockupVersion')), 5)

        manager = IVersionManager(self.root.content.get_editable())
        self.assertTrue(manager.delete())

        self.assertEqual(self.root.content.get_editable(), None)
        self.assertEqual(len(self.root.content.objectIds('MockupVersion')), 4)

    def test_delete_published_version(self):
        """Delete a published version. This is not possible and should
        trigger an error.
        """
        self.assertEqual(len(self.root.content.objectIds('MockupVersion')), 5)

        manager = IVersionManager(self.root.content.get_viewable())
        with self.assertRaises(VersioningError):
            manager.delete()

        self.assertEqual(len(self.root.content.objectIds('MockupVersion')), 5)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionManagerTestCase))
    return suite
