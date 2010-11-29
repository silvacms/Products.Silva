# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import unittest

# Silva
from silva.core import interfaces
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest

from Products.Silva.icon import IconRegistry, registry, get_icon_url
from Products.Silva.testing import FunctionalLayer


class IconRegistryTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile('pdf', 'PDF File')
        factory.manage_addFile('text', 'Text File')
        self.root.pdf.set_content_type('application/pdf')
        self.root.text.set_content_type('text/plain')

    def test_get_icon_url(self):
        """Test usefull function get_icon_url
        """
        request = TestRequest()
        self.assertEqual(
            get_icon_url(self.root, request),
            u'http://localhost/root/misc_/Silva/silva.png')
        self.assertEqual(
            get_icon_url(self.root.pdf, request),
            u'http://localhost/root/++resource++silva.icons/file_pdf.png')
        self.assertEqual(
            get_icon_url(self.root.text, request),
            u'http://localhost/root/++resource++silva.icons/file_txt.png')

    def test_default_icons(self):
        """Test default registered icons.
        """
        # Silva content types
        self.assertEqual(
            registry.getIcon(self.root),
            'misc_/Silva/silva.png')
        self.assertEqual(
            registry.getIconByIdentifier(('meta_type', 'Silva Link')),
            'misc_/Silva/link.png' )

        # Simple member icons
        member = self.root.service_members.get_member('author')
        self.assertEqual(
            registry.getIcon(member),
            'misc_/Silva/member.png')

    def test_registry(self):
        """Test registry
        """
        self.assertEquals(
            self.root.pdf.get_mime_type(), 'application/pdf')
        self.assertEquals(
            self.root.text.get_mime_type(), 'text/plain')

        registry = IconRegistry()
        self.failUnless(verifyObject(interfaces.IIconRegistry, registry))

        registry.registerIcon(('meta_type', 'Silva Root'), 'root.png')
        registry.registerIcon(('mime_type', 'text/plain'), 'file_text.png')
        registry.registerIcon(
            ('mime_type', 'application/octet-stream'), 'file.png')
        registry.registerIcon(('mime_type', 'application/pdf'), 'file_pdf.png')

        self.assertEquals(
            registry.getIconByIdentifier(('meta_type', 'Silva Root')),
            'root.png')
        self.assertEquals(
            registry.getIconByIdentifier(
                ('mime_type', 'application/octet-stream')),
            'file.png')
        self.assertRaises(
            ValueError, registry.getIconByIdentifier, ('meta_type', 'Foo Bar'))

        self.assertEquals(registry.getIcon(self.root), 'root.png')
        self.assertEquals(registry.getIcon(self.root.pdf), 'file_pdf.png')
        self.assertEquals(registry.getIcon(self.root.text), 'file_text.png')
        self.assertRaises(ValueError, registry.getIcon, TestRequest())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IconRegistryTestCase))
    return suite

