import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from Products.Silva import convert

class ConvertRegistry(SilvaTestCase.SilvaTestCase):
    def setUp(self):
        self.reg = convert.Registry()

    def test_direct_path(self):
        def factory(*args):
            return lambda *args: 'x to y'

        self.reg.set_loader(factory, 'x-1.0', 'y-1.0')
        t = self.reg.get_converter('x-1.0', 'y-1.0')
        self.assertEquals(t(''), 'x to y')

    def test_unknown_fromid(self):
        self.assertRaises(
            convert.UnknownId, 
            self.reg.get_converter, 'no-1.0', 'silva-1.0'
        )

    def test_unknown_toid(self):
        self.reg.set_loader(lambda: None, 'x-1.0', 'y-1.0')
        self.assertRaises(
            convert.UnknownId,
            convert.get_converter, 'x-1.0', 'no-1.0'
            )

    def test_unknown_version(self):
        self.reg.set_loader(lambda: None, 'some-1.0', 'other-1.0')
        self.assertRaises(
            convert.UnknownVersion,
            convert.get_converter, 'some-1.0', 'other-1.1'
            )

    def test_no_conversion_path(self):
        self.reg.set_loader(lambda: None, 'x-1.0', 'y-1.0')
        self.reg.set_loader(lambda: None, 'y-1.1', 'x-1.0')
        self.assertRaises(
            convert.NoConversionPath,
            convert.get_converter, 'x-1.0', 'y-1.1')


    def test_split_ident(self):
        res = convert.split_ident('x-1.0')
        self.assertEquals(res, ('x', ('1', '0')))
        res = convert.split_ident('x-1.0.3')
        self.assertEquals(res, ('x', ('1', '0', '3')))

    def test_split_ident_error(self):
        self.assertRaises(
            convert.FormatError,
            convert.split_ident,
            'x123123')

    def test_convert_list(self):
        factory = lambda *args: None

        self.reg.set_loader(factory, 'x-2.0', 'y-3.0')
        self.reg.set_loader(factory, 'y-3.0', 'z-2.5')
        self.reg.set_loader(factory, 'z-2.5', 'x-3.5')

        l = self.reg.get_converter_list('x-2.0', 'x-3.5')
        self.assertEquals(len(l),3)

    def test_chaining(self):
        class conv:
            def __init__(self, source, target):
                self.source_id, self.source_version = source
                self.target_id, self.target_version = target

            def __call__(self, obj):
                return "%s %s-%s" % (obj, self.source_id, self.target_id)

        self.reg.set_loader(conv, 'x-2.0', 'y-3.0')
        self.reg.set_loader(conv, 'y-3.0', 'z-2.5')

        c = self.reg.get_converter('x-2.0', 'z-2.5')

        res = c('')
        self.assertEquals(res.strip(), 'x-y y-z')


class ShortestPath(SilvaTestCase.SilvaTestCase):

    def test_simple_path(self):
        G = { 'x' : {'y': 1, 'z': 1},
              'z' : {'a' : 1}}

        l = convert.find_shortest_path(G, 'x', 'a')
        self.assertEquals(l, ['x','z','a'])

    def test_no_path(self):
        G = { 'x' : {'y': 1, 'z': 1},
              'z' : {'a' : 1}}

        self.assertEquals(
            len(convert.find_shortest_path(G, 'a', 'h')),
            0)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ConvertRegistry))
        suite.addTest(unittest.makeSuite(ShortestPath))
        return suite
