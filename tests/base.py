import unittest
import Zope
Zope.startup()

from security import OmnipotentUser
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from security import PermissiveSecurityPolicy, AnonymousUser

# this needs to be imported after startup?
from Testing.makerequest import makerequest

class SilvaTestCase(unittest.TestCase):
    """silva unit tests should be based on this
    
        NOTE: it'll be slow :/
    """    
    
    def setUp(self):
        try:
            _policy = PermissiveSecurityPolicy()
            self._oldPolicy = setSecurityPolicy(_policy)
            self.connection = connection = Zope.DB.open()
            root = connection.root()['Application']
            newSecurityManager(None, AnonymousUser().__of__(root))
            root = makerequest(root)
            self.root = root
            root.URL1 = ''
            root.REQUEST.AUTHENTICATED_USER = OmnipotentUser()
            root.manage_addProduct['Silva'].manage_addRoot(
                'silva_test', 'Silva Test')
            root.silva_test.service_extensions.install('SilvaDocument')
            self.silva = root.silva_test
        except:
            self.tearDown()
            raise

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
        noSecurityManager()
        setSecurityPolicy(self._oldPolicy)

    def addObject(self, container, type_name, id, product='Silva',
            **kw):
        getattr(container.manage_addProduct[product],
            'manage_add%s' % type_name)(id, **kw)
        return getattr(container, id)


