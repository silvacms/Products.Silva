# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.Image.utils import Size
from Products.Silva.Image.utils import WHResizeSpec, PercentResizeSpec

class MockImage(object):

    def get_size(self):
        return (1000, 1000)


class ImageUtilsTestCase(unittest.TestCase):

    def test_size(self):
        """Test Size.
        """
        size = Size(10, 10)
        self.assertEqual(size, (10, 10)) # You can compare it to a tuple.
        self.assertNotEqual(size, (15, 10))

    def test_percentresizespec(self):
        """Test PercentResizeSpec used to express a resize specification.
        """
        # Tet parse
        self.assertEqual(PercentResizeSpec.parse('foo'), None)
        self.assertEqual(PercentResizeSpec.parse('foo%'), None)
        self.assertEqual(PercentResizeSpec.parse('foo1%'), None)
        self.assertNotEqual(PercentResizeSpec.parse('10%'), None)
        self.assertNotEqual(PercentResizeSpec.parse('10.5%'), None)
        # test get_size
        self.assertEqual(
            PercentResizeSpec.parse('10%').get_size(MockImage()),
            Size(100, 100))
        self.assertEqual(
            PercentResizeSpec.parse('20.5%').get_size(MockImage()),
            Size(205, 205))
        self.assertEqual(
            PercentResizeSpec.parse('300%').get_size(MockImage()),
            Size(3000, 3000))

    def test_whresizespec(self):
        """Test WHResizeSpec used to express a resize specification.
        """
        # Test parse
        self.assertEqual(WHResizeSpec.parse('foo'), None)
        self.assertEqual(WHResizeSpec.parse('fooxfoo'), None)
        self.assertEqual(WHResizeSpec.parse('*x*'), None)
        self.assertEqual(WHResizeSpec.parse('*X*'), None)
        self.assertEqual(WHResizeSpec.parse('*200x200'), None)
        self.assertEqual(WHResizeSpec.parse('200x200foo'), None)
        self.assertNotEqual(WHResizeSpec.parse('*X500'), None)
        self.assertNotEqual(WHResizeSpec.parse('500X*'), None)
        self.assertNotEqual(WHResizeSpec.parse('*x500'), None)
        self.assertNotEqual(WHResizeSpec.parse('500x*'), None)
        self.assertNotEqual(WHResizeSpec.parse('600x500'), None)
        self.assertNotEqual(WHResizeSpec.parse('500x600'), None)
        # Test get_size
        self.assertEqual(
            WHResizeSpec.parse('500x500').get_size(MockImage()),
            Size(500, 500))
        self.assertEqual(
            WHResizeSpec.parse('500x600').get_size(MockImage()),
            Size(500, 600))
        self.assertEqual(
            WHResizeSpec.parse('600X400').get_size(MockImage()),
            Size(600, 400))
        self.assertEqual(
            WHResizeSpec.parse('*X400').get_size(MockImage()),
            Size(400, 400))
        self.assertEqual(
            WHResizeSpec.parse('3000x*').get_size(MockImage()),
            Size(3000, 3000))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImageUtilsTestCase))
    return suite
