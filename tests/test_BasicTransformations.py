# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
#
# Testing of xml<->xhtml bidrectional conversions.
# this tests along with the module is intended to 
# work with python2.1 and python2.2 or better
# 
# $Revision: 1.1 $
import unittest

# 
# module setup
#
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO 

try:
    from xml.parsers import expat 
except ImportError:
    from xml.parsers.pyexpat import expat

import sys,os

try:
    sys.path.insert(0, '..')
    from transform.ObjectParser import ObjectParser
    from transform.eopro2_11 import silva
except ImportError:
    from Products.Silva.transform.ObjectParser import ObjectParser
    from Products.Silva.transform.eopro2_11 import silva

# lazy, but in the end we want to test everything anyway

from xml.dom import minidom
#
# getting test content
#

def get_test_content(name):
    """ get testing content from the 'files' directory
    """
    tmp = os.path.dirname(os.path.abspath(sys.argv[0]))
    fn = os.path.join(tmp, 'files', name)
    f = open(fn, 'rb')
    s = f.read()
    f.close()
    return s


class SilvaXMLObjectParser(unittest.TestCase):
    """ See that Construction of the object tree from silva-xml works """
    def setUp(self):
        self.parser = ObjectParser(silva)

        self.basicdoc = '''<silva_document id="test">
                                <title>testtitle</title>
                                <doc/>
                             </silva_document>'''

    def find_exactly_one(self, node, tag):
        res = node.find(tag)
        self.assert_(len(res)==1)
        return res[0]

    def test_silva_basic_document(self):
        node = self.parser.parse(self.basicdoc)
        self.assert_(not self.parser.unknown)
        node = self.find_exactly_one(node, 'silva_document')
        self.assert_(node.attrs['id'] == 'test')
        title = self.find_exactly_one(node, 'title')
        self.assert_(title.content.asBytes()=='testtitle')
        self.find_exactly_one(node, 'doc')

    def test_processinginst(self):
        """ test that processing instruction goes through the parser """
        node = self.parser.parse('<?xml version="1.0" encoding="UTF-8" ?><silva_document/>')
        self.assert_(node.find('silva_document'))

    def test_attribute(self):
        """ test that attribute lookup basically works """
        node = self.parser.parse('<silva_document id="whatever"/>')
        node = node[0]
        self.assert_(node.attrs._id)
        self.assert_(node.attrs['id'])
        try: node.attrs['notexists']
        except KeyError: pass
        else: 
            raise AssertionError, "access to non-existent attribute didn't raise exception"
        try: node.attrs._notexists
        except AttributeError: pass
        else: 
            raise AssertionError, "access to non-existent attribute didn't raise exception"

    def test_inequality_operator(self):
        s1= '<silva_document><title>my title</title></silva_document>'
        s2= ' <silva_document>  <title>my title</title></silva_document>'
        node1 = self.parser.parse(s1)
        node2 = self.parser.parse(s2)
        self.assert_(node1 != node2)

    def test_equality_operator(self):
        s1= '<silva_document><title>my title</title></silva_document>'
        s2= '<silva_document><title>my title</title></silva_document>'
        node1 = self.parser.parse(s1)
        node2 = self.parser.parse(s2)
        self.assert_(node1==node1)
        self.assert_(node1==node2)

    def test_plain_text_as_content_with_asBytes(self):
        s1= '<p type="normal">blabla</p>'
        node1 = self.parser.parse(s1)

        p = node1.find('p')[0]
        node2 = p.__class__(
            'mytext',
            type = p.attrs._type
            )
        self.assert_(node2.content.asBytes()=='mytext')

    def test_method_find(self):
        node = self.parser.parse(self.basicdoc)

        self.assert_(node.find('silva_document'))
        self.assertEquals(node.find('silva_document'),
                          node.find(silva.silva_document))
        sdoc = node.find('silva_document')[0]
        self.assert_(sdoc.find('doc'))
        self.assertEquals(sdoc.find('doc'),
                          sdoc.find(silva.doc))

    def test_method_compact(self):
        node= self.parser.parse(self.basicdoc)
        self.assert_(node.compact())
       
    def test_simple_dogfood_roundtrip(self):
        node= self.parser.parse(self.basicdoc)
        # looses processing instruction
        newstring = node.asBytes()
        node2 = self.parser.parse(newstring)
        self.assert_(node==node2)

    def test_method_compact(self):
        node= self.parser.parse(self.basicdoc)
        self.assert_(node.compact())
        # should traverse the tree


#
# invocation of test suite
#
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaXMLObjectParser))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
