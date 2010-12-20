from unittest import TestCase, TestSuite, main, makeSuite

import dav

# enter the host's settings in the 'config' file
from ConfigParser import ConfigParser
config = ConfigParser()
config.read('config')

class WebDAVBaseTestCase(TestCase):
    """DAV test case"""

    def connect(self, login=False):
        """Create a WebDAV connection"""
        davcon = dav.DAVConnection(config.get('server', 'host'), 
                                    config.get('server', 'dav_port'))
        username = config.get('server', 'manager_username')
        passwd = ''
        if login:
            passwd = config.get('server', 'manager_password')
        davcon.set_auth(username, passwd)
        return davcon
        
    def setUp(self):
        self.basepath = config.get('server', 'basepath')
        
        self.slvcontents = '<doc><p type="normal">Some contents</p></doc>'
        self.xmlcontents = '<doc><foo /></doc>'

        self.connect(True).put('%s/doc.slv' % self.basepath, 
                                self.slvcontents,
                                content_type='text/xml')

        self.connect(True).mkcol('%s/some_folder' % self.basepath)

        self.connect(True).put('%s/some_folder/test.xml' % self.basepath, 
                                self.xmlcontents,
                                content_type='text/xml')

        if hasattr(self, 'afterSetUp'):
            self.afterSetUp()

    def tearDown(self):
        if hasattr(self, 'beforeTearDown'):
            self.beforeTearDown()
        self.connect(True).delete('%s/some_folder/test.xml' % self.basepath)
        self.connect(True).delete('%s/some_folder' % self.basepath)
        self.connect(True).delete('%s/doc.slv' % self.basepath)

    def assertContains(self, col, value):
        """Assert whether 'value' is in 'col'"""
        if not value in col:
            raise self.failureException, '%s doesn\'t contain %s' % \
                    (col, value)

    def assertLacks(self, col, value):
        """Assert whether 'value' is in 'col'"""
        if value in col:
            raise self.failureException, '%s not lacking %s' % (col, value)

class WebDAVTestCase(WebDAVBaseTestCase):

    def beforeTearDown(self):
        res = self.connect(True).delete('%s/other_doc.slv' % self.basepath)
        res = self.connect(True).delete('%s/doc_copy.slv' % self.basepath)
        res = self.connect(True).delete('%s/some_folder_copy' % self.basepath)

    def test_get_put(self):
        res = self.connect().get('%s/doesntexist' % self.basepath)
        self.assertEquals(res.status, 404)
    
        res = self.connect().get('%s/doc.slv' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect(True).get('%s/doc.slv' % self.basepath)
        self.assertEquals(res.status, 200)
        self.assertEquals(res.read(), self.slvcontents)

        res = self.connect().get('%s/some_folder/test.xml' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect(True).get('%s/some_folder/test.xml' % self.basepath)
        self.assertEquals(res.status, 200)

        res = self.connect().put('%s/other_doc.slv' % self.basepath,
                                    self.slvcontents)
        self.assertEquals(res.status, 401)

        res = self.connect(True).put('%s/other_doc.slv' % self.basepath,
                                        self.slvcontents)
        self.assertEquals(res.status, 201)

        res = self.connect(True).get('%s/other_doc.slv' % self.basepath)
        self.assertEquals(res.status, 200)
        self.assertEquals(res.read(), self.slvcontents)

    def test_mkcol(self):
        res = self.connect(True).propfind('%s/some_new_folder' % self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect(True).mkcol('%s/some_new_folder' % self.basepath)
        self.assertEquals(res.status, 201)

        res = self.connect().propfind('%s/some_new_folder' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect(True).propfind('%s/some_new_folder' % self.basepath)
        self.assertEquals(res.status, 207)

        res = self.connect(True).delete('%s/some_new_folder' % self.basepath)
        self.assertEquals(res.status, 204)

        res = self.connect(True).propfind('%s/some_new_folder' % self.basepath)
        self.assertEquals(res.status, 404)

    def test_propfind_propset(self):
        proppatch_body = ('<?xml version="1.0" ?>\n'
                            '<D:propertyupdate xmlns:D="DAV:" xmlns="foo:">'
                            '<D:set>'
                            '<D:prop>'
                            '<foo>foo</foo>'
                            '</D:prop>'
                            '</D:set>'
                            '</D:propertyupdate>')

        res = self.connect().propfind('%s/doc.slv' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect().proppatch('%s/doc.slv' % self.basepath,
                                        proppatch_body)
        self.assertEquals(res.status, 401)

        res = self.connect().propfind('%s/some_folder' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect().proppatch('%s/some_folder' % self.basepath,
                                        proppatch_body)
        self.assertEquals(res.status, 401)

        res = self.connect(True).propfind('%s/doc.slv' % self.basepath)
        self.assertEquals(res.status, 207)

        res = self.connect(True).propfind('%s/some_folder' % self.basepath)
        self.assertEquals(res.status, 207)

        # proppatch isn't supported (yet?)
        res = self.connect(True).proppatch('%s/doc.slv' % self.basepath,
                                        proppatch_body)
        self.assertEquals(res.status, 409)

        res = self.connect(True).proppatch('%s/some_folder' % self.basepath,
                                        proppatch_body)
        self.assertEquals(res.status, 409)

    def test_options(self):
        # not only test OPTIONS, also a sanity check to see if Zope still
        # returns the same list for collections and non-collection resources
        allowed = ['OPTIONS', 'TRACE', 'GET', 'HEAD', 'POST', 'PUT', 'COPY', 
                    'MOVE', 'DELETE', 'MKCOL', 'LOCK', 'UNLOCK', 'PROPFIND', 
                    'PROPPATCH']
        allowed.sort()
        
        res = self.connect().options(self.basepath)
        self.assertEquals(res.status, 200)
        allow = res.getheader('allow')
        allow = [a.strip() for a in allow.split(',')]
        allow.sort()
        self.assertEquals(allow, allowed)

        res = self.connect().options('%s/some_folder/test.xml' % self.basepath)
        self.assertEquals(res.status, 200)
        allow = res.getheader('allow')
        allow = [a.strip() for a in allow.split(',')]
        allow.sort()
        self.assertEquals(allow, allowed)

    def test_copy(self):
        res = self.connect().copy('%s/doc.slv' % self.basepath,
                                    '%s/doc_copy.slv' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect(True).get('%s/doc_copy.slv' % self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect(True).copy('%s/doc.slv' % self.basepath,
                                        '%s/doc_copy.slv' % self.basepath)
        self.assertContains([200, 201, 204], res.status)

        res = self.connect(True).get('%s/doc_copy.slv' % self.basepath)
        self.assertEquals(res.status, 200)

        res = self.connect().copy('%s/some_folder' % self.basepath,
                                    '%s/some_folder_copy' % self.basepath)
        self.assertContains([401, 403], res.status)

        res = self.connect(True).propfind('%s/some_folder_copy' % 
                                            self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect(True).copy('%s/some_folder' % self.basepath,
                                        '%s/some_folder_copy' % self.basepath)
        self.assertContains([200, 201, 204], res.status)

        res = self.connect(True).propfind('%s/some_folder_copy' % 
                                            self.basepath)
        self.assertEquals(res.status, 207)

    def test_move(self):
        res = self.connect().move('%s/doc.slv' % self.basepath,
                                    '%s/doc_copy.slv' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect(True).get('%s/doc_copy.slv' % self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect(True).move('%s/doc.slv' % self.basepath,
                                        '%s/doc_copy.slv' % self.basepath)
        self.assertContains([200, 201, 204], res.status)

        res = self.connect(True).get('%s/doc.slv' % self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect(True).get('%s/doc_copy.slv' % self.basepath)
        self.assertEquals(res.status, 200)

        res = self.connect().move('%s/some_folder' % self.basepath,
                                    '%s/some_folder_copy' % self.basepath)
        self.assertContains([401, 403], res.status)

        res = self.connect(True).propfind('%s/some_folder_copy' % 
                                            self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect(True).move('%s/some_folder' % self.basepath,
                                        '%s/some_folder_copy' % self.basepath)
        self.assertContains([200, 201, 204], res.status)

        res = self.connect(True).propfind('%s/some_folder' % self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect(True).propfind('%s/some_folder_copy' % 
                                            self.basepath)
        self.assertEquals(res.status, 207)

    def test_delete(self):
        res = self.connect().delete('%s/doc.slv' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect(True).delete('%s/doc.slv' % self.basepath)
        self.assertContains([200, 204], res.status)

        res = self.connect(True).get('%s/doc.slv' % self.basepath)
        self.assertEquals(res.status, 404)

        res = self.connect().delete('%s/some_folder' % self.basepath)
        self.assertEquals(res.status, 401)

        res = self.connect(True).delete('%s/some_folder' % self.basepath)
        self.assertContains([200, 204], res.status)
        
        res = self.connect(True).propfind('%s/some_folder' % self.basepath)
        self.assertEquals(res.status, 404)

if __name__ == '__main__':
    main()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(WebDAVTestCase, 'test'))
        return suite

