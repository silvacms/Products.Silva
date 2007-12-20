

import unittest
from zope.testing import doctest

from SilvaTestCase import SilvaFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite


OPTIONS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

def test_suite():

    simplefolderadd = FunctionalDocFileSuite('funit/simplefolderadd.txt',
                                             test_class=SilvaFunctionalTestCase,
                                             optionflags=OPTIONS,
                                             )
    suite = unittest.TestSuite()
    suite.addTest(simplefolderadd)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


