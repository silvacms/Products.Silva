# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$
import SilvaTestCase

from Products.Silva.adapters import subscribable
from Products.Silva import Indexer

from BTrees.OOBTree import OOBTree

class SubscribableTestCase(SilvaTestCase.SilvaTestCase):
    """Test the Subscribable adapter.
    """
    def afterSetUp(self):
        """Content tree:

        /publication
        /publication/folder
        /publication/folder/doc
        /ghost
        /link

        """
        self.publication = self.add_publication(self.root, 'publication', u'Test Publication')
        self.folder = self.add_folder(self.publication, 'folder', u'Test Folder')
        self.doc = self.add_document(self.folder, 'doc', u'Test Document')
        self.ghost = self.add_ghost(self.root, 'ghost', None)
        self.link = self.add_link(self.root, 'link', u'Test Link', 'url')
        self.image = self.add_image(self.root, 'image', u'Test Image')
        Indexer.manage_addIndexer(self.root, 'indexer', 'Test Indexer')
        self.indexer = self.root.indexer

    def test_getSubscribable(self):
        subscr = subscribable.getSubscribable(self.root)
        self.assert_(isinstance(subscr, subscribable.SubscribableRoot))
        subscr = subscribable.getSubscribable(self.publication)
        self.assert_(isinstance(subscr, subscribable.Subscribable))
        subscr = subscribable.getSubscribable(self.folder)
        self.assert_(isinstance(subscr, subscribable.Subscribable))
        subscr = subscribable.getSubscribable(self.doc)
        self.assert_(isinstance(subscr, subscribable.Subscribable))
        subscr = subscribable.getSubscribable(self.ghost)
        self.assert_(isinstance(subscr, subscribable.Subscribable))
        subscr = subscribable.getSubscribable(self.link)
        self.assert_(isinstance(subscr, subscribable.Subscribable))
        subscr = subscribable.getSubscribable(self.image)
        self.assertEquals(None, subscr)
        subscr = subscribable.getSubscribable(self.indexer)
        self.assertEquals(None, subscr)

    def test_subscribability(self):
        subscr = subscribable.getSubscribable(self.doc)
        # content aqcuires subscribability by default
        self.assertEquals(
            subscribable.ACQUIRE_SUBSCRIBABILITY, subscr.subscribability())
        # now make content subscribable
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        self.assertEquals(subscribable.SUBSCRIBABLE, subscr.subscribability())
        # and make it not subscribable anymore
        subscr.setSubscribability(subscribable.NOT_SUBSCRIBABLE)
        self.assertEquals(subscribable.NOT_SUBSCRIBABLE, subscr.subscribability())

    def test__buildSubscribablesList(self):
        # first make root subscribable (acquired by the contained objects)
        rootsubscr = subscribable.getSubscribable(self.root)
        rootsubscr.setSubscribability(subscribable.SUBSCRIBABLE)
        subscr = subscribable.getSubscribable(self.root.publication.folder.doc)
        expected = [self.doc, self.folder, self.publication, self.root,]
        subscribables = subscr._buildSubscribablesList()
        contexts = [o.context for o in subscribables]
        self.assertEquals(expected, contexts)
        #
        rootsubscr = subscribable.getSubscribable(self.root)
        rootsubscr.setSubscribability(subscribable.NOT_SUBSCRIBABLE)
        pubsubscr = subscribable.getSubscribable(self.root.publication)
        pubsubscr.setSubscribability(subscribable.SUBSCRIBABLE)
        subscr = subscribable.getSubscribable(self.root.publication.folder.doc)
        expected = [self.doc, self.folder, self.publication,]
        subscribables = subscr._buildSubscribablesList()
        contexts = [o.context for o in subscribables]
        self.assertEquals(expected, contexts)
        #
        rootsubscr = subscribable.getSubscribable(self.root)
        rootsubscr.setSubscribability(subscribable.NOT_SUBSCRIBABLE)
        pubsubscr = subscribable.getSubscribable(self.root.publication)
        pubsubscr.setSubscribability(subscribable.NOT_SUBSCRIBABLE)
        foldersubscr = subscribable.getSubscribable(self.root.publication.folder)
        foldersubscr.setSubscribability(subscribable.SUBSCRIBABLE)
        subscr = subscribable.getSubscribable(self.root.publication.folder.doc)
        expected = [self.doc, self.folder,]
        subscribables = subscr._buildSubscribablesList()
        contexts = [o.context for o in subscribables]
        self.assertEquals(expected, contexts)
        #
        rootsubscr = subscribable.getSubscribable(self.root)
        rootsubscr.setSubscribability(subscribable.NOT_SUBSCRIBABLE)
        pubsubscr = subscribable.getSubscribable(self.root.publication)
        pubsubscr.setSubscribability(subscribable.ACQUIRE_SUBSCRIBABILITY)
        foldersubscr = subscribable.getSubscribable(self.root.publication.folder)
        foldersubscr.setSubscribability(subscribable.SUBSCRIBABLE)
        subscr = subscribable.getSubscribable(self.root.publication.folder.doc)
        expected = [self.doc, self.folder,]
        subscribables = subscr._buildSubscribablesList()
        contexts = [o.context for o in subscribables]
        self.assertEquals(expected, contexts)

    def test_getSubscriptions(self):
        d = {'foo@bar.baz':None, 'baz@bar.baz':None, 'qux@bar.baz':None}
        self.doc.__subscriptions__ = OOBTree(d)
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        subscriptions = subscr.getSubscriptions()
        expected = d.keys()
        expected.sort()
        emailaddresses = [s.emailaddress() for s in subscriptions]
        emailaddresses.sort()
        self.assertEquals(expected, emailaddresses)
        contentsubscribedtos = [s.contentSubscribedTo() for s in subscriptions]
        expected = [self.doc, self.doc, self.doc]
        self.assertEquals(expected, contentsubscribedtos)

    def test_subscribe(self):
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        l = ['foo@bar.baz', 'baz@bar.baz', 'qux@bar.baz']
        l.sort()
        for addr in l:
            subscr.subscribe(addr)
        subscriptions = subscr.getSubscriptions()
        emailaddresses = [o.emailaddress() for o in subscriptions]
        emailaddresses.sort()
        self.assertEquals(l, emailaddresses)

    def test_unsubscribe(self):
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        d = {'foo@bar.baz':None, 'baz@bar.baz':None, 'qux@bar.baz':None}
        self.doc.__subscriptions__ = OOBTree(d)
        for addr in d.keys():
            subscr.unsubscribe(addr)
        subscriptions = subscr.getSubscriptions()
        emailaddresses = [o.emailaddress() for o in subscriptions]
        self.assertEquals([], emailaddresses)

    def test_generateConfirmationToken(self):
        # We just test whether two subsequently generated tokens are not
        # identical
        subscr = subscribable.getSubscribable(self.doc)
        token1 = subscr.generateConfirmationToken('foo@bar.baz')
        token2 = subscr.generateConfirmationToken('foo2@bar.baz')
        self.assertNotEquals(token1, token2)

    def test_isValidSubscription(self):
        subscr = subscribable.getSubscribable(self.doc)
        addr = "foo@bar.baz"
        token = subscr.generateConfirmationToken(addr)
        self.assertEquals(True, subscr.isValidSubscription(addr, token))
        # Subsequent use of the same token is not valid
        self.assertEquals(False, subscr.isValidSubscription(addr, token))
        # Invalid token is not valid (duh!)
        self.assertEquals(
            False, subscr.isValidSubscription(addr, token + 'foobar'))
        addr = "foob@bar.baz"
        self.assertEquals(False, subscr.isValidSubscription(addr, token))

    def test_isValidCancellation(self):
        subscr = subscribable.getSubscribable(self.doc)
        addr = "foo@bar.baz"
        token = subscr.generateConfirmationToken(addr)
        self.assertEquals(True, subscr.isValidCancellation(addr, token))
        # Subsequent use of the same token is not valid
        self.assertEquals(False, subscr.isValidCancellation(addr, token))
        # Invalid token is not valid (duh!)
        self.assertEquals(
            False, subscr.isValidCancellation(addr, token + 'foobar'))
        addr = "foob@bar.baz"
        self.assertEquals(False, subscr.isValidCancellation(addr, token))

    def test_isSubscribed(self):
        subscr = subscribable.getSubscribable(self.doc)
        addr = "foo@bar.baz"
        subscr.subscribe(addr)
        self.assert_(subscr.isSubscribed(addr))

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SubscribableTestCase))
    return suite
