# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Acquisition import aq_chain

from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IGhost, IGhostVersion
from silva.core.interfaces import IContainerManager, IPublicationWorkflow
from silva.core.references.reference import BrokenReferenceError
from silva.core.references.interfaces import IReferenceService, IReferenceValue


class GhostTestCase(unittest.TestCase):
    """Test the Ghost object.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addImage('image', 'Image')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', 'Ghost')

    def test_ghost(self):
        """Test simple ghost creation.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', 'Ghost', haunted=self.root.document)

        version = self.root.ghost.get_editable()
        self.assertTrue(verifyObject(IGhost, self.root.ghost))
        self.assertTrue(verifyObject(IGhostVersion, version))

        self.assertEqual(version.get_haunted(), self.root.document)
        self.assertEqual(
            aq_chain(version.get_haunted()),
            aq_chain(self.root.document))
        self.assertEqual(version.get_link_status(), None)

        manager = IContainerManager(self.root)
        with self.assertRaises(BrokenReferenceError):
            with manager.deleter() as deleter:
                deleter.add(self.root.document)

    def test_ghost_reference(self):
        """Test the reference created by the ghost.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', 'Ghost', haunted=self.root.document)

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

    def test_ghost_title(self):
        """Test ghost get_title. It should return the title of the target.
        """
        # XXX I don't think those are expected results ...
        # XXX Add get_short_title to the test as well
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', 'Ghost')

        self.root.ghost.get_editable().set_haunted(self.root.document)
        self.assertEqual(self.root.ghost.get_title_editable(), 'Document')
        self.assertEqual(self.root.ghost.get_short_title(), 'document')
        self.assertEqual(self.root.ghost.get_title(), '')

        IPublicationWorkflow(self.root.document).publish()
        self.assertEqual(self.root.ghost.get_title_editable(), 'Document')
        self.assertEqual(self.root.ghost.get_short_title(), 'Document')
        self.assertEqual(self.root.ghost.get_title(), '')

        IPublicationWorkflow(self.root.ghost).publish()
        self.assertEqual(self.root.ghost.get_title_editable(), 'Document')
        self.assertEqual(self.root.ghost.get_short_title(), 'Document')
        self.assertEqual(self.root.ghost.get_title(), 'Document')

        IPublicationWorkflow(self.root.document).close()
        self.assertEqual(self.root.ghost.get_title_editable(), 'Document')
        self.assertEqual(self.root.ghost.get_short_title(), 'document')
        self.assertEqual(self.root.ghost.get_title(), '')

        self.root.ghost.get_viewable().set_haunted(0)
        self.assertEqual(
            self.root.ghost.get_title_editable(),
            u'Ghost target is broken')
        self.assertEqual(
            self.root.ghost.get_short_title(),
            u'Ghost target is broken')
        self.assertEqual(
            self.root.ghost.get_title(),
            u'Ghost target is broken')

    def test_ghost_is_published(self):
        """Test whenever a Ghost is published or not. This depends if
        the ghosted content is published or not.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', 'Ghost')
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
        factory.manage_addGhost('ghost', 'Ghost')

        version = self.root.ghost.get_editable()
        self.assertEqual(version.get_link_status(), version.LINK_EMPTY)

        version.set_haunted(self.root.folder)
        self.assertEqual(version.get_link_status(), version.LINK_FOLDER)

        version.set_haunted(self.root.folder.ghost)
        self.assertEqual(version.get_link_status(), version.LINK_GHOST)

        version.set_haunted(self.root.image)
        self.assertEqual(version.get_link_status(), version.LINK_NO_CONTENT)

        version.set_haunted(self.root.ghost)
        self.assertEqual(version.get_link_status(), version.LINK_CIRC)

        version.set_haunted(self.root.document)
        self.assertEqual(version.get_link_status(), version.LINK_OK)

        version.set_haunted(0)
        self.assertEqual(version.get_link_status(), version.LINK_EMPTY)

    def test_ghost_modification_time(self):
        """Test that the ghost modification_time is the same than the
        document.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('ghost', 'Ghost')
        self.assertEqual(self.root.ghost.get_modification_datetime(), None)

        self.root.ghost.get_editable().set_haunted(self.root.document)
        self.assertEqual(
            self.root.ghost.get_modification_datetime(),
            self.root.document.get_modification_datetime())

        self.root.ghost.get_editable().set_haunted(0)
        self.assertEqual(self.root.ghost.get_modification_datetime(), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostTestCase))
    return suite
