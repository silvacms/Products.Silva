from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

# Expected tab properties
contents = []
preview = []
properties = []
access = []
publish = []

contents.append('contents')
contents.append('add a new item')
preview.append('preview')
preview.append('see the content in the public layout:')
properties.append('properties')
properties.append('various settings:')
access.append('access')
access.append('restrict access to users with a specific role')
publish.append('publish')
publish.append('publishing actions')

class NavigateTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                       MixinRoleContent, MixinNavigate):
    """
        test navigation tabs as manager at Silva root
    """

    def test_content_tab(self):
        self.do_navigate(SilvaTestCase.user_manager, success, contents)
    
    def test_preview_tab(self):
        self.do_navigate(SilvaTestCase.user_manager, success, preview)
    
    def test_properties_tab(self):
        self.do_navigate(SilvaTestCase.user_manager, success, properties)
        
    def test_access_tab(self):
        self.do_navigate(SilvaTestCase.user_manager, success, access)

    def test_publish_tab(self):
        self.do_navigate(SilvaTestCase.user_manager, success, publish)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NavigateTestCase))
    return suite
