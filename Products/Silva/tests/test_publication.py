# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IPublicationWorkflow
from zope.interface.verify import verifyObject


class MockupVersion(Version):
    meta_type='MockupVersion'


class MockupVersionedContent(VersionedContent):
    meta_type='MockupVersionedContent'

    def __init__(self, *args):
        super(MockupVersionedContent, self).__init__(*args)
        self._setObject('0', MockupVersion('0'))
        self.create_version('0', None, None)


class PublicationWorkflowTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.root._setObject('content', MockupVersionedContent('content'))

    def test_implementation(self):
        publisher = IPublicationWorkflow(self.root, None)
        self.assertEqual(publisher, None)

        publisher = IPublicationWorkflow(self.root.content, None)
        self.assertNotEqual(publisher, None)
        self.assertTrue(verifyObject(IPublicationWorkflow, publisher))

    def test_publish_unapproved(self):
        content = self.root.content
        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')

        publisher = IPublicationWorkflow(content)
        publisher.publish()

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublicationWorkflowTestCase))
    return suite
