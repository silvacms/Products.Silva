# Copyright (c) 2002, 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_helpers.py,v 1.1 2003/03/26 11:46:58 clemens Exp $

import unittest

import Zope
Zope.startup()
from Products.Silva import helpers



class HelpersTest(unittest.TestCase):
    """ actually the code tested by this tests is not there
    to stay, but as it is around for a while, it could get regular tests as well ;-)
    """
   
    def test_parser(self):
        testString = r"""
        property: value1, "my quote, comma containing value", 
        "another value with \"quotes\" in it, as well as commas", "something containing \\", even more;

property2: aha, what's that, ";;;" ,,,'ignores commas',"",;

single: only one property  ;

white: "  one property,  whitespace preserving   ";

"""

        props = {'property': ['value1','my quote, comma containing value',
                              'another value with "quotes" in it, as well as commas',
                              'something containing \\', 'even more'] ,
                 'property2': [ 'aha', "what's that", ';;;', "'ignores commas'",'' ] ,
                 'single' : [ 'only one property' ],
                 'white' : ["  one property,  whitespace preserving   "],
                 }
                          
        props_parsed = helpers._parse_raw(testString)

        self.assertEquals(props, props_parsed)
    
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HelpersTest))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
