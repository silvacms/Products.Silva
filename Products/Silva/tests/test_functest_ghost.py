# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings
from Products.Silva.tests.helpers import publish_object
from silva.core.references.reference import get_content_id


class BaseTest(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        factory = self.root.publication.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document title')
        self.document = self.root.publication.document

        self.layer.logout()
        self.browser = self.layer.get_web_browser(smi_settings)
        self.browser.login('manager', 'manager')


class TestGhostAdd(BaseTest):

    def goto_add_form(self):
        self.assertEqual(self.browser.open('/root/edit'), 200)

        form = self.browser.get_form('md.container')
        form.get_control('md.container.field.content').value = 'Silva Ghost'
        self.assertEqual(form.submit('md.container.action.new'), 200)
        self.assertEqual(self.browser.url, '/root/edit/+/Silva Ghost')

        return self.browser.get_form('addform')

    def test_add_ghost_save(self):
        document_id = get_content_id(self.document)
        form = self.goto_add_form()
        form.get_control("addform.field.id").value = 'someghost'
        form.get_control("addform.field.haunted").value = document_id
        self.assertEqual(form.submit(name='addform.action.save'), 200)

        self.assertTrue('someghost' in self.root.objectIds())
        self.assertEqual(self.browser.inspect.feedback, ['Added Silva Ghost.'])
        self.assertEqual(self.browser.url, '/root/edit')

    def test_add_ghost_save_and_edit(self):
        document_id = get_content_id(self.document)
        form = self.goto_add_form()
        form.get_control("addform.field.id").value = 'someghost'
        form.get_control("addform.field.haunted").value = document_id
        self.assertEqual(form.submit(name='addform.action.save_edit'), 200)

        self.assertTrue('someghost' in self.root.objectIds())
        self.assertEqual(self.browser.inspect.feedback, ['Added Silva Ghost.'])
        self.assertEqual(self.browser.url, '/root/someghost/edit')

    def test_add_ghost_cancel(self):
        form = self.goto_add_form()
        self.assertEqual(form.submit(name="addform.action.cancel"), 200)

        self.assertFalse('someghost' in self.root.objectIds())
        self.assertEqual(self.browser.inspect.feedback, [])
        self.assertEqual(self.browser.url, '/root/edit')


class TestGhostEdit(BaseTest):

    def setUp(self):
        super(TestGhostEdit, self).setUp()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None, haunted=self.document)
        self.ghost = self.root.ghost

        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('other', 'Other document')
        self.other = self.root.other

    def goto_form(self):
        path = "/".join(self.ghost.getPhysicalPath())
        self.assertEqual(self.browser.open(path + '/edit'), 200)
        return self.browser.get_form('editform')

    def test_edit_form(self):
        form = self.goto_form()
        reference_field = form.get_control("editform.field.haunted")
        self.assertEquals(
            reference_field.value,
            str(get_content_id(self.document)),
            "reference field value should be the intid of the document")

    def test_edit_form_set_new_haunted(self):
        form = self.goto_form()
        other_id = get_content_id(self.other)
        form.get_control('editform.field.haunted').value = other_id
        self.assertEqual(form.submit(name='editform.action.save-changes'), 200)

        self.assertEqual(self.browser.inspect.feedback, ['Changes saved.'])
        version = self.ghost.get_editable()
        self.assertEqual(version.get_haunted(), self.other)


class TestGhostViewBase(BaseTest):

    def setUp(self):
        super(TestGhostViewBase, self).setUp()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('docghost', None, haunted=self.document)
        self.ghost = self.root.docghost


class TestGhostViewNotPublished(TestGhostViewBase):

    def test_view_before_publish(self):
        self.browser.open('/root/docghost')
        self.assertEquals('200 OK', self.browser.status)
        self.assertTrue('is not viewable' in self.browser.contents)
        self.assertTrue('Document title' not in self.browser.contents)

    def test_preview_as_admin_before_publish(self):
        self.browser.open('/root/++preview++/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('is broken' in self.browser.contents)


class TestGhostViewGhostPublished(TestGhostViewBase):

    def setUp(self):
        super(TestGhostViewGhostPublished, self).setUp()
        publish_object(self.ghost)

    def test_view(self):
        """ The ghost is published but not the document
        so the ghost is broken
        """
        self.browser.open('/root/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('is broken' in self.browser.contents)


class TestGhostViewGhostAndDocPublished(TestGhostViewGhostPublished):

    def setUp(self):
        super(TestGhostViewGhostAndDocPublished, self).setUp()
        publish_object(self.document)

    def test_view(self):
        self.browser.open('/root/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('Document title' in self.browser.contents)

    def test_preview_as_admin_before_publish(self):
        self.browser.open('/root/++preview++/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('Document title' in self.browser.contents)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGhostAdd))
    suite.addTest(unittest.makeSuite(TestGhostEdit))
    suite.addTest(unittest.makeSuite(TestGhostViewNotPublished))
    suite.addTest(unittest.makeSuite(TestGhostViewGhostPublished))
    suite.addTest(unittest.makeSuite(TestGhostViewGhostAndDocPublished))
    return suite
