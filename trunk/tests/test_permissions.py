from AccessControl import Unauthorized
from DateTime import DateTime
import SilvaTestCase

class RestrictedPythonTest(SilvaTestCase.SilvaTestCase):
    """Mixin class to test whether things are allowed from Python.
    """

        
    def addPythonScript(self, id, params='', body=''):
        #try:
        #    self.silva._getObj('testscript')
        #    self.silva.manage_delObjects(['testscript'])
        #except AttributeError:
        #    pass
        factory = self.silva.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript(id)
        self.silva[id].ZPythonScript_edit(params, body)

    def check(self, body):
        self.addPythonScript('testscript', body=body)
        try:
            self.silva.testscript()
        except (ImportError, Unauthorized), e:
            self.fail(e)

    def checkUnauthorized(self, body):
        self.addPythonScript('testscript', body=body)
        try:
            self.silva.testscript()
        except (AttributeError, Unauthorized):
            pass
        else:
            self.fail("Authorized but shouldn't be")
            
class DocumentPublicationTestCase(RestrictedPythonTest):
    def afterSetUp(self):
        uf = self.silva.acl_users
        uf._doAddUser('anon', 'secret', [], [])
        uf._doAddUser('viewer', 'secret', ['Viewer'], [])
        uf._doAddUser('manager', 'secret', ['Manager'], [])

    def test_unpublished(self):
        self.add_document(self.silva, 'alpha', 'Alpha')
        self.login('anon')
        self.check('context.alpha.view()')

    def test_published_empty(self):
        self.add_document(self.silva, 'alpha', 'Alpha')
        doc = self.silva.alpha
        doc.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        doc.approve_version()
        self.login('anon')
        self.check('context.alpha.view()')

    def test_published_with_paragraph(self):
        self.add_document(self.silva, 'alpha', 'Alpha')
        doc = self.silva.alpha
        # add a paragraph to doc
        doc['0'].content.manage_edit('<doc><p>Test</p></doc>')
        doc.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        doc.approve_version()
        self.login('anon')
        self.check('context.alpha.view()')

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentPublicationTestCase))
    return suite
