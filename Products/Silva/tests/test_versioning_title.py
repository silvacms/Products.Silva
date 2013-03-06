# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IPublicationWorkflow

from Products.Silva.testing import FunctionalLayer


class VersioningTitleTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Title')

    def test_set_title(self):
        document = self.root.document
        self.assertEqual(document.get_title(), '')
        self.assertEqual(document.get_title_or_id(), 'document')
        self.assertEqual(document.get_title_editable(), 'Title')
        self.assertEqual(document.get_title_or_id_editable(), 'Title')

        document.set_title('Other Title')
        self.assertEqual(document.get_title(), '')
        self.assertEqual(document.get_title_or_id(), 'document')
        self.assertEqual(document.get_title_editable(), 'Other Title')
        self.assertEqual(document.get_title_or_id_editable(), 'Other Title')

    def test_set_title_while_published(self):
        document = self.root.document
        IPublicationWorkflow(document).publish()

        self.assertEqual(document.get_title(), 'Title')
        self.assertEqual(document.get_title_or_id(), 'Title')
        self.assertEqual(document.get_title_editable(), 'Title')
        self.assertEqual(document.get_title_or_id_editable(), 'Title')

        document.set_title('Other Title')
        self.assertEqual(document.get_title(), 'Title')
        self.assertEqual(document.get_title_or_id(), 'Title')
        self.assertEqual(document.get_title_editable(), 'Title')
        self.assertEqual(document.get_title_or_id_editable(), 'Title')

    def test_set_title_while_new_version(self):
        document = self.root.document
        IPublicationWorkflow(document).publish()
        IPublicationWorkflow(document).new_version()
        version = document.get_editable()

        self.assertEqual(document.get_title(), 'Title')
        self.assertEqual(document.get_title_or_id(), 'Title')
        self.assertEqual(document.get_title_editable(), 'Title')
        self.assertEqual(document.get_title_or_id_editable(), 'Title')

        document.set_title('Other Title')
        self.assertEqual(document.get_title(), 'Title')
        self.assertEqual(document.get_title_or_id(), 'Title')
        self.assertEqual(document.get_title_editable(), 'Other Title')
        self.assertEqual(document.get_title_or_id_editable(), 'Other Title')
        self.assertEqual(version.get_title(), 'Other Title')

    def test_set_title_on_version(self):
        document = self.root.document
        version = document.get_editable()

        version.set_title('Version Title')

        self.assertEqual(document.get_title(), '')
        self.assertEqual(document.get_title_or_id(), 'document')
        self.assertEqual(document.get_title_editable(), 'Version Title')
        self.assertEqual(document.get_title_or_id_editable(), 'Version Title')
        self.assertEqual(version.get_title(), 'Version Title')

    def test_get_short_title(self):
        document = self.root.document

        self.assertEqual(document.get_short_title(), 'document')
        self.assertEqual(document.get_short_title_editable(), 'Title')

        IPublicationWorkflow(document).publish()

        self.assertEqual(document.get_short_title(), 'Title')
        self.assertEqual(document.get_short_title_editable(), 'Title')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersioningTitleTestCase))
    return suite
