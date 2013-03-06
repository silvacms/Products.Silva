# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from DateTime import DateTime
from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IVersionManager, VersioningError
from zope.interface.verify import verifyObject


class VersionManagerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')

        publisher = IPublicationWorkflow(self.root.test)
        for version_id in range(1, 5):
            publisher.publish()
            publisher.new_version()

        self.layer.login('author')

    def test_implementation(self):
        published = self.root.test.get_viewable()
        manager = IVersionManager(published)
        self.assertTrue(verifyObject(IVersionManager, manager))

    def test_get_publication_datetime(self):
        """Verify get_publication_datetime
        """
        manager = IVersionManager(self.root.test.get_editable())
        self.assertEqual(manager.get_publication_datetime(), None)

        now = DateTime()
        self.root.test.set_unapproved_version_publication_datetime(now)
        self.assertEqual(manager.get_publication_datetime(), now)

        # Published version already have a publication date since they
        # are published.
        manager = IVersionManager(self.root.test.get_viewable())
        self.assertNotEqual(manager.get_publication_datetime(), None)

    def test_get_expiration_datetime(self):
        """Verify get_expiration_datetime
        """
        manager = IVersionManager(self.root.test.get_editable())
        self.assertEqual(manager.get_expiration_datetime(), None)

        now = DateTime()
        self.root.test.set_unapproved_version_expiration_datetime(now)
        self.assertEqual(manager.get_expiration_datetime(), now)

    def test_get_last_author(self):
        """Return the last author who change the version.
        """
        manager = IVersionManager(self.root.test.get_viewable())
        self.assertNotEqual(manager.get_last_author(), 'editor')

    def test_delete_unapproved_version(self):
        """Delete an unapproved version.
        """
        content = self.root.test
        self.assertEqual(len(content.objectIds('Mockup Version')), 5)

        manager = IVersionManager(content.get_editable())
        self.assertTrue(manager.delete())

        self.assertEqual(content.get_editable(), None)
        self.assertEqual(len(content.objectIds('Mockup Version')), 4)

    def test_delete_published_version(self):
        """Delete a published version. This is not possible and should
        trigger an error.
        """
        content = self.root.test
        self.assertEqual(len(content.objectIds('Mockup Version')), 5)

        manager = IVersionManager(content.get_viewable())
        with self.assertRaises(VersioningError):
            manager.delete()

        self.assertEqual(len(content.objectIds('Mockup Version')), 5)

    def test_delete_closed_version(self):
        """Delete a previously closed version.
        """
        content = self.root.test
        self.assertEqual(len(content.objectIds('Mockup Version')), 5)

        manager = IVersionManager(content.get_mockup_version(0))
        manager.delete()

        self.assertEqual(len(content.objectIds('Mockup Version')), 4)

        manager = IVersionManager(content.get_mockup_version(1))
        manager.delete()

        self.assertEqual(len(content.objectIds('Mockup Version')), 3)

    def test_get_status(self):
        """Get status of different version.
        """
        content = self.root.test
        manager = IVersionManager(content.get_mockup_version(1))
        self.assertEqual(manager.get_status(), 'closed')

        manager = IVersionManager(content.get_mockup_version(2))
        self.assertEqual(manager.get_status(), 'last_closed')

        manager = IVersionManager(content.get_mockup_version(3))
        self.assertEqual(manager.get_status(), 'published')

        manager = IVersionManager(content.get_mockup_version(4))
        self.assertEqual(manager.get_status(), 'unapproved')

    def test_make_editable_with_unapproved(self):
        """Make an old version editable while having an unapproved
        version.
        """
        content = self.root.test
        manager = IVersionManager(content.get_mockup_version(1))
        self.assertTrue(manager.make_editable())
        self.assertEqual(len(content.objectIds('Mockup Version')), 6)

    def test_make_editable_with_approved(self):
        """Make an old version editable while having an approved and
        yet not published version. This will not work.
        """
        content = self.root.test

        self.layer.login('editor')

        publisher = IPublicationWorkflow(content)
        publisher.approve(DateTime() + 50)

        self.layer.login('author')

        manager = IVersionManager(content.get_mockup_version(1))
        with self.assertRaises(VersioningError):
            manager.make_editable()
        self.assertEqual(len(content.objectIds('Mockup Version')), 5)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionManagerTestCase))
    return suite
