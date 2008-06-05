import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class QuotaTestCase(SilvaFunctionalTestCase):
    """
       login manager
       enable quota
       put on file
       check parameters/settings screen
       set a quota
       check changes
       go back on contents
       add a folder
       add a publication
       add a folder
       add a file
       add a publication
       go on parameters/settings screen
       check acquired quota
       put a correct quota
       check screen
       put 0/empty quota
       check screen
       put an invalid quota
       check screen (should get an error)
    """


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuotaTestCase))
    return suite

