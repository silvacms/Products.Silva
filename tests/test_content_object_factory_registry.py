# Copyright (c) 2003-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
import SilvaTestCase

from Products.Silva.ContentObjectFactoryRegistry import \
        contentObjectFactoryRegistry

class ContentObjectFactoryRegistryTestCase(SilvaTestCase.SilvaTestCase):
    """Test case for some contentObjectFactoryRegistry stuff"""

    def afterSetUp(self):
        self.dummy_factory = lambda id, ct, body: False

        contentObjectFactoryRegistry._registry = []
        contentObjectFactoryRegistry._ordered = None

    def test_order(self):
        """test the order mechanism"""
        # add some registrations and order a couple of times, see if the
        # order matches our expectations

        # first some really straightforward stuff
        contentObjectFactoryRegistry.registerFactory(
            self.dummy_factory, 'bar', 'foo')

        contentObjectFactoryRegistry.registerFactory(
            self.dummy_factory, 'foo', -1)

        contentObjectFactoryRegistry._order()
        ordered_ids = [x[1] for x in contentObjectFactoryRegistry._ordered]
        
        self.assertEquals(ordered_ids, ['foo', 'bar'])

        # remove the _ordered attribute from the registry so we can test again
        #contentObjectFactoryRegistry._ordered = None

        # let's first test a bit with a problem where a factory gets 
        # registered with a before that doesn't yet exist
        contentObjectFactoryRegistry.registerFactory(
            self.dummy_factory, 'baz', 'qux')

        self.assertRaises(ValueError, contentObjectFactoryRegistry._order)

        # remove the last registration (shouldn't be done from code, so we
        # don't have a dedicated method or anything)
        contentObjectFactoryRegistry._registry.pop()

        # just to be sure see if it does work now
        contentObjectFactoryRegistry._order()

        # remove the _ordered attribute again
        #contentObjectFactoryRegistry._ordered = None

        # now make it a bit harder, let's create a circular reference 
        # (which should lead to an exception)
        contentObjectFactoryRegistry.registerFactory(
            self.dummy_factory, 'baz', 'bar')

        contentObjectFactoryRegistry._registry.pop(0)
        contentObjectFactoryRegistry.registerFactory(
            self.dummy_factory, 'foo', 'baz')

        self.assertRaises(ValueError, contentObjectFactoryRegistry._order)

    def test_getObjectFor(self):
        # now for some more serious work let's test the actual getter
        class Foo:
            pass
        factory1 = lambda context, id, content_type, body: Foo()
        checker1 = lambda id, content_type, body: True
        
        contentObjectFactoryRegistry.registerFactory(factory1, checker1)

        class Bar:
            pass
        factory2 = lambda context, id, content_type, body: Bar()
        checker2 = lambda id, content_type, body: (content_type == 'bar' or content_type == 'baz')

        contentObjectFactoryRegistry.registerFactory(factory2, checker2)

        class Baz:
            pass
        factory3 = lambda context, id, content_type, body: Baz()
        checker3 = lambda id, content_type, body: (content_type == 'baz')

        contentObjectFactoryRegistry.registerFactory(factory3, checker3, checker2)

        obj1 = contentObjectFactoryRegistry.getObjectFor(None, 'someid', 'foo', '')
        self.assert_(isinstance(obj1, Foo))

        obj2 = contentObjectFactoryRegistry.getObjectFor(None, 'someid', 'bar', '')
        self.assert_(isinstance(obj2, Bar))

        obj3 = contentObjectFactoryRegistry.getObjectFor(None, 'someid', 'baz', '')
        self.assert_(isinstance(obj3, Baz))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentObjectFactoryRegistryTestCase))
    return suite
