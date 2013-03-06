# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Python
import unittest

# Silva
from silva.core import interfaces
from silva.core.interfaces.adapters import IIconResolver
from zope.component import queryAdapter
from zope.interface.verify import verifyObject

from Products.Silva.icon import IconRegistry, registry
from Products.Silva.testing import FunctionalLayer, TestRequest


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

    def test_icon_url(self):
        """Test adapter to retrieve icon urls'.
        """
        resolver = queryAdapter(TestRequest(), IIconResolver)
        self.assertTrue(verifyObject(IIconResolver, resolver))

        self.assertEqual(
            resolver.get_content(self.root),
            '++resource++icon-Silva-Root.png')
        self.assertEqual(
            resolver.get_content_url(self.root),
            'http://localhost/root/++resource++icon-Silva-Root.png')
        self.assertEqual(
            resolver.get_identifier('Silva Root'),
            '++resource++icon-Silva-Root.png')
        self.assertEqual(
            resolver.get_identifier_url('Silva Root'),
            'http://localhost/root/++resource++icon-Silva-Root.png')

        self.assertEqual(
            resolver.get_content(self.root.pdf),
            '++static++/silva.icons/file_pdf.png')
        self.assertEqual(
            resolver.get_content_url(self.root.pdf),
            'http://localhost/root/++static++/silva.icons/file_pdf.png')
        self.assertEqual(
            resolver.get_content(self.root.text),
            '++static++/silva.icons/file_txt.png')
        self.assertEqual(
            resolver.get_content_url(self.root.text),
            'http://localhost/root/++static++/silva.icons/file_txt.png')

    def test_icon_tag(self):
        """Test usefull function used to access icon tags.
        """
        resolver = queryAdapter(TestRequest(), IIconResolver)
        self.assertTrue(verifyObject(IIconResolver, resolver))

        self.assertEqual(
            resolver.get_tag(self.root),
            '<img height="16" width="16" src="http://localhost/root/++resource++icon-Silva-Root.png" alt="Silva Root" />')
        self.assertEqual(
            resolver.get_tag(content=self.root),
            '<img height="16" width="16" src="http://localhost/root/++resource++icon-Silva-Root.png" alt="Silva Root" />')
        self.assertEqual(
            resolver.get_tag(identifier='Silva Root'),
            '<img height="16" width="16" src="http://localhost/root/++resource++icon-Silva-Root.png" alt="Silva Root" />')
        self.assertEqual(
            resolver.get_tag(identifier='default'),
            '<img height="16" width="16" src="http://localhost/root/++static++/silva.icons/silvageneric.gif" alt="default" />')
        self.assertEqual(
            resolver.get_tag(),
            '<img height="16" width="16" src="http://localhost/root/++static++/silva.icons/missing.png" alt="Missing" />')


    def test_default_icons(self):
        """Test default registered icons.
        """
        # Silva content types
        self.assertEqual(
            registry.get_icon(self.root),
            '++resource++icon-Silva-Root.png')
        self.assertEqual(
            registry.get_icon_by_identifier(
                ('meta_type', 'Silva Link')),
            '++resource++icon-Silva-Link.png' )

        # Simple member icons
        member = self.root.service_members.get_member('author')
        self.assertEqual(
            registry.get_icon(member),
            '++resource++icon-Silva-Simple-Member.png')

        # File icons
        self.assertEqual(
            registry.get_icon(self.root.pdf),
            '++static++/silva.icons/file_pdf.png')
        self.assertEqual(
            registry.get_icon(self.root.text),
            '++static++/silva.icons/file_txt.png')

    def test_member_gravatar(self):
        """Test that if you ask the icon for a member you can a
        gravatar icon.
        """
        # XXX This will will be implemented in Silva 3.1
        # self.assertXMLEqual(
        #     user.avatar_tag(),
        #     '<img src="' + self.root.get_root_url() + '/globals/avatar.png" alt="manager\'s avatar" title="manager\'s avatar" style="height: 32px; width: 32px" />')
        # user.set_email('user@example.com')
        # self.assertEqual('user@example.com', user.avatar())
        # self.assertXMLEqual(
        #     user.avatar_tag(),
        #     '<img src="https://secure.gravatar.com/avatar.php?default=' + urllib.quote(self.root.get_root_url(),'') + '%2Fglobals%2Favatar.png&size=32&gravatar_id=b58996c504c5638798eb6b511e6f49af" alt="manager\'s avatar" title="manager\'s avatar" style="height: 32px; width: 32px" />')

    def test_registry(self):
        """Test registry
        """
        self.assertEqual(
            self.root.pdf.get_mime_type(), 'application/pdf')
        self.assertEqual(
            self.root.text.get_mime_type(), 'text/plain')

        registry = IconRegistry()
        self.assertTrue(verifyObject(interfaces.IIconRegistry, registry))

        registry.register(
            ('meta_type', 'Silva Root'), 'root.png')
        registry.register(
            ('mime_type', 'text/plain'), 'file_text.png')
        registry.register(
            ('mime_type', 'application/octet-stream'), 'file.png')
        registry.register(
            ('mime_type', 'application/pdf'), 'file_pdf.png')

        self.assertEqual(
            registry.get_icon_by_identifier(
                ('meta_type', 'Silva Root')),
            'root.png')
        self.assertEqual(
            registry.get_icon_by_identifier(
                ('mime_type', 'application/octet-stream')),
            'file.png')
        with self.assertRaises(ValueError):
            registry.get_icon_by_identifier(('meta_type', 'Foo Bar'),)

        self.assertEqual(registry.get_icon(self.root), 'root.png')
        self.assertEqual(registry.get_icon(self.root.pdf), 'file_pdf.png')
        self.assertEqual(registry.get_icon(self.root.text), 'file_text.png')
        with self.assertRaises(ValueError):
            registry.get_icon(TestRequest())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IconRegistryTestCase))
    return suite

