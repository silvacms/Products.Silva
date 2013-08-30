# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import transaction

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Acquisition import aq_chain
from DateTime import DateTime
from Products.Silva.testing import FunctionalLayer, Transaction
from Products.Silva.ftesting import public_settings
from Products.SilvaMetadata.interfaces import IMetadataService, ReadOnlyError

from silva.core.interfaces.errors import ContentError
from silva.core.interfaces import errors
from silva.core.interfaces import IGhost, IGhostVersion, IAccessSecurity
from silva.core.interfaces import IContainerManager, IPublicationWorkflow
from silva.core.references.interfaces import IReferenceService, IReferenceValue


class GhostTestCase(unittest.TestCase):
    """Test the Ghost object.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')
            factory.manage_addFolder('folder', 'Folder')
            factory.manage_addImage('image', 'Image')

            factory = self.root.folder.manage_addProduct['Silva']
            factory.manage_addGhost('ghost', None)

        editable = self.root.document.get_editable()
        metadata = getUtility(IMetadataService).getMetadata(editable)
        metadata.setValues(
            'silva-extra',
            {'modificationtime': DateTime('2011-04-25T12:00:00Z')})
        transaction.commit()

    def test_ghost(self):
        """Test simple ghost creation and life time.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None, haunted=self.root.document)

        version = self.root.ghost.get_editable()
        self.assertTrue(verifyObject(IGhost, self.root.ghost))
        self.assertTrue(verifyObject(IGhostVersion, version))

        self.assertEqual(version.get_link_status(), None)
        self.assertEqual(version.get_haunted(), self.root.document)
        self.assertEqual(
            aq_chain(version.get_haunted()),
            aq_chain(self.root.document))

        manager = IContainerManager(self.root)
        with manager.deleter() as deleter:
            deleter(self.root.document)

        self.assertEqual(version.get_haunted(), None)
        self.assertEqual(version.get_link_status(), errors.EmptyInvalidTarget())

    def test_reference(self):
        """Test the reference created by the ghost.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None, haunted=self.root.document)

        ghost = self.root.ghost.get_editable()
        reference = getUtility(IReferenceService).get_reference(
            ghost, name=u"haunted")
        self.assertTrue(verifyObject(IReferenceValue, reference))
        self.assertEqual(
            aq_chain(reference.target),
            aq_chain(self.root.document))
        self.assertEqual(
            aq_chain(reference.source),
            aq_chain(ghost))

        manager = IContainerManager(self.root)
        with manager.deleter() as deleter:
            deleter(self.root.document)

        reference = getUtility(IReferenceService).get_reference(
            ghost, name=u"haunted")
        self.assertEqual(reference, None)

    def test_metadata(self):
        """If you ask metadata about a ghost, you should get the
        metadata about the haunted content, if available.
        """
        service = getUtility(IMetadataService)
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None)

        ghost = self.root.ghost
        document = self.root.document

        # Our ghost is broken, so we have no metadata
        self.assertEqual(service.getMetadata(ghost), None)

        ghost.get_editable().set_haunted(document)
        # The document is not published, the Ghost don't have access
        # to the document metadata.
        self.assertEqual(service.getMetadata(ghost), None)

        IPublicationWorkflow(document).publish()
        # Now it should work, you should get the metadata of the document
        ghost_binding = service.getMetadata(ghost)
        self.assertNotEqual(ghost_binding, None)
        self.assertEqual(
            ghost_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(ghost, 'silva-content', 'maintitle'),
            u"Document")

        # You can't change the value
        with self.assertRaises(ReadOnlyError):
            ghost_binding.setValues('silva-content', {'maintitle': u'Ghost'})

        # Nothing changed
        ghost_binding = service.getMetadata(ghost)
        self.assertEqual(
            ghost_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(ghost, 'silva-content', 'maintitle'),
            u"Document")

        # Update document metadata
        document_binding = service.getMetadata(document.get_viewable())
        document_binding.setValues('silva-content', {'maintitle': u"Changed"})

        # You should see the values from the ghost point of view.
        ghost_binding = service.getMetadata(ghost)
        self.assertEqual(
            ghost_binding.get('silva-content', 'maintitle'),
            u"Changed")
        self.assertEqual(
            service.getMetadataValue(ghost, 'silva-content', 'maintitle'),
            u"Changed")

    def test_version_metadata(self):
        """If you ask metadata about a ghost version, you should get
        the metadata about the haunted content, if available.
        """
        service = getUtility(IMetadataService)
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None)

        ghost = self.root.ghost.get_editable()
        document = self.root.document

        # Our ghost is broken, so we have no metadata
        self.assertEqual(service.getMetadata(ghost), None)

        ghost.get_editable().set_haunted(document)
        # The document is not published, the Ghost don't have access
        # to the document metadata.
        self.assertEqual(service.getMetadata(ghost), None)

        IPublicationWorkflow(document).publish()
        # Now it should work, you should get the metadata of the document
        ghost_binding = service.getMetadata(ghost)
        self.assertNotEqual(ghost_binding, None)
        self.assertEqual(
            ghost_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(ghost, 'silva-content', 'maintitle'),
            u"Document")

        # You can't change the value.
        with self.assertRaises(ReadOnlyError):
            ghost_binding.setValues('silva-content', {'maintitle': u'Ghost'})

        # Nothing changed.
        ghost_binding = service.getMetadata(ghost)
        self.assertEqual(
            ghost_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(ghost, 'silva-content', 'maintitle'),
            u"Document")

        # Update document metadata
        document_binding = service.getMetadata(document.get_viewable())
        document_binding.setValues('silva-content', {'maintitle': u"Changed"})

        # You should see the values from the ghost point of view.
        ghost_binding = service.getMetadata(ghost)
        self.assertEqual(
            ghost_binding.get('silva-content', 'maintitle'),
            u"Changed")
        self.assertEqual(
            service.getMetadataValue(ghost, 'silva-content', 'maintitle'),
            u"Changed")

    def test_set_title(self):
        """Test ghost set_title. It should just trigger an error.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None, target=self.root.document)

        # None is authorized as a title, because that is the value
        # that it must passed to the factory.
        self.root.ghost.set_title(None)

        # Other value should raise an error
        with self.assertRaises(ContentError):
            self.root.ghost.set_title('Ghost')

        # You sould be able to rename a ghost with the IContainerManager
        with IContainerManager(self.root).renamer() as renamer:
            self.assertEqual(
                renamer((self.root.ghost, 'ghost', None)),
                self.root.ghost)

        # But not to change its title.
        with IContainerManager(self.root).renamer() as renamer:
            self.assertIsInstance(
                renamer((self.root.ghost, 'ghost', 'Ghost')),
                ContentError)

    def test_get_title(self):
        """Test ghost get_title. It should return the title of the target.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None)
        ghost = self.root.ghost
        target = self.root.document

        ghost.get_editable().set_haunted(target)
        self.assertEqual(ghost.get_short_title_editable(), 'Document')
        self.assertEqual(ghost.get_short_title(), 'ghost')
        self.assertEqual(ghost.get_title_editable(), 'Document')
        self.assertEqual(ghost.get_title(), '')
        self.assertEqual(ghost.get_title_or_id(), 'ghost')

        IPublicationWorkflow(target).publish()
        self.assertEqual(ghost.get_short_title_editable(), 'Document')
        self.assertEqual(ghost.get_short_title(), 'ghost')
        self.assertEqual(ghost.get_title_editable(), 'Document')
        self.assertEqual(ghost.get_title(), '')
        self.assertEqual(ghost.get_title_or_id(), 'ghost')

        IPublicationWorkflow(ghost).publish()
        self.assertEqual(ghost.get_short_title_editable(), 'Document')
        self.assertEqual(ghost.get_short_title(), 'Document')
        self.assertEqual(ghost.get_title_editable(), 'Document')
        self.assertEqual(ghost.get_title(), 'Document')
        self.assertEqual(ghost.get_title_or_id(), 'Document')

        IPublicationWorkflow(target).close()
        self.assertEqual(ghost.get_short_title_editable(), 'Document')
        self.assertEqual(ghost.get_short_title(), 'Ghost target is broken')
        self.assertEqual(ghost.get_title_editable(), 'Document')
        self.assertEqual(ghost.get_title(), 'Ghost target is broken')
        self.assertEqual(ghost.get_title_or_id(), 'Ghost target is broken')

        ghost.get_viewable().set_haunted(0)
        self.assertEqual(ghost.get_short_title_editable(), 'Ghost target is broken')
        self.assertEqual(ghost.get_short_title(), 'Ghost target is broken')
        self.assertEqual(ghost.get_title_editable(), 'Ghost target is broken')
        self.assertEqual(ghost.get_title(), 'Ghost target is broken')
        self.assertEqual(ghost.get_title_or_id(), 'Ghost target is broken')

    def test_is_published(self):
        """Test whenever a Ghost is published or not. This depends if
        the ghosted content is published or not.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None)
        self.assertFalse(self.root.ghost.is_published())

        IPublicationWorkflow(self.root.ghost).publish()
        self.assertFalse(self.root.ghost.is_published())
        self.assertEqual(self.root.ghost.get_editable(), None)

        self.root.ghost.get_viewable().set_haunted(self.root.document)
        self.assertFalse(self.root.ghost.is_published())

        IPublicationWorkflow(self.root.document).publish()
        self.assertTrue(self.root.ghost.is_published())

        IPublicationWorkflow(self.root.document).close()
        self.assertFalse(self.root.ghost.is_published())

    def test_ghost_link_status(self):
        """Test ghost get_link_status.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', None)

        version = self.root.ghost.get_editable()
        self.assertEqual(
            version.get_link_status(),
            errors.EmptyInvalidTarget())

        version.set_haunted(self.root.folder)
        self.assertEqual(
            version.get_link_status(),
            errors.ContentInvalidTarget())

        version.set_haunted(self.root.folder.ghost)
        self.assertEqual(
            version.get_link_status(),
            errors.GhostInvalidTarget())

        version.set_haunted(self.root.image)
        self.assertEqual(
            version.get_link_status(),
            errors.ContentInvalidTarget())

        version.set_haunted(self.root.ghost)
        self.assertEqual(
            version.get_link_status(),
            errors.CircularInvalidTarget())

        version.set_haunted(self.root.document)
        self.assertEqual(
            version.get_link_status(),
            None)

        version.set_haunted(0)
        self.assertEqual(
            version.get_link_status(),
            errors.EmptyInvalidTarget())

    def test_modification_time(self):
        """Test that the ghost modification_time is the same than the
        document.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addGhost('ghost', None)
        ghost = self.root.ghost
        target = self.root.document
        self.assertEqual(ghost.get_modification_datetime(), None)

        with Transaction():
            ghost.get_editable().set_haunted(target)
        self.assertEqual(ghost.get_modification_datetime(), None)

        with Transaction():
            IPublicationWorkflow(ghost).publish()
        self.assertEqual(
            ghost.get_modification_datetime(),
            target.get_modification_datetime())

        with Transaction():
            IPublicationWorkflow(ghost).new_version()
            ghost.get_editable().set_haunted(0)
        self.assertEqual(       # We still see publlised version
            ghost.get_modification_datetime(),
            target.get_modification_datetime())

        with Transaction():
            IPublicationWorkflow(ghost).publish()
        self.assertEqual(ghost.get_modification_datetime(), None)

    def test_head_request(self):
        """Test HEAD requests on Ghosts.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addGhost('ghost', None, haunted=self.root.document)

        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/ghost', method='HEAD'), 200)
            self.assertEqual(
                browser.headers['Content-Type'],
                'text/html;charset=utf-8')
            # The ghost is broken, there is no modification date.
            self.assertNotIn('Last-Modified', browser.headers)

        with Transaction():
            IPublicationWorkflow(self.root.ghost).publish()

        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/ghost', method='HEAD'), 200)
            self.assertEqual(
                browser.headers['Content-Type'],
                'text/html;charset=utf-8')
            # We see the modification date from the document.
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Mon, 25 Apr 2011 12:00:00 GMT')
            self.assertEqual(len(browser.contents), 0)

    def test_render_protected_content(self):
        """Test rendering a protected content.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addLink(
                'link', 'Infrae', relative=False, url='http://infrae.com')
            factory.manage_addGhost('ghost', None, haunted=self.root.link)

            IAccessSecurity(self.root.link).minimum_role = 'Viewer'
            IPublicationWorkflow(self.root.link).publish()
            IPublicationWorkflow(self.root.ghost).publish()

        with self.layer.get_browser(public_settings) as browser:
            browser.options.follow_redirect = False
            self.assertEqual(
                browser.open('/root/ghost'),
                401)
            self.assertEqual(
                browser.inspect.title,
                ['Protected area'])
            browser.login('viewer')
            self.assertEqual(
                browser.open('/root/ghost'),
                302)
            self.assertEqual(
                browser.headers['Location'],
                'http://infrae.com')

    def test_render_closed_content(self):
        """Test rendering a ghost that points to a content that is
        closed.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addLink(
                'link', 'Infrae', relative=False, url='http://infrae.com')
            factory.manage_addGhost('ghost', None, haunted=self.root.link)

            IPublicationWorkflow(self.root.link).publish()
            IPublicationWorkflow(self.root.ghost).publish()

        with self.layer.get_browser(public_settings) as browser:
            browser.options.follow_redirect = False
            self.assertEqual(
                browser.open('/root/ghost'),
                302)
            self.assertEqual(
                browser.headers['Location'],
                'http://infrae.com')

        with Transaction():
            IPublicationWorkflow(self.root.link).close()
        with self.layer.get_browser(public_settings) as browser:
            browser.options.follow_redirect = False
            self.assertEqual(
                browser.open('/root/ghost'),
                200)
            self.assertEqual(
                browser.inspect.content,
                ["This content is unavailable. Please inform the site manager."])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostTestCase))
    return suite
