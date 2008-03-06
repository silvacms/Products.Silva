import unittest

from SilvaTestCase import SilvaFunctionalTestCase
from SilvaBrowser import SilvaBrowser

class SilvaBrowserTest(SilvaFunctionalTestCase):
    """
        test the SilvaBrowser API methods
    """
    def test_silvabrowser(self):
        """initialize the SilvaBrowser API"""
        sb = SilvaBrowser()

    def test_login_logout(self):
        """
            go()
            login()
            click_href_labeled()
        """
        # login
        sb = SilvaBrowser()
        # goto silva root
        status, url = sb.go(self.silva_url)
        self.assertEquals(status, 200)
        # goto edit page
        status, url = sb.go(sb.smi_url())
        self.assertEquals(status, 401)
        # besides the 401, url will be None, 
        # since we didn't go anywhere
        #self.assertEquals(url, None)
        # login fake user
        #status, url = sb.login(sb.smi_url(), 'skdgsdkj', 'zxcmnbvx')
        #self.assertEquals(status, 401)
        # login manager
        #status, url = sb.login('manager', 'secret', sb.smi_url())
        #self.assertEquals(status, 200)
        # logout
        #status, url = sb.click_href_labeled('logout Manager manager')
        #self.assertEquals(status, 401)
    
    #def test_delete_published_content(self):
    #    """
    #        test
    #        get_content()
    #        select_content()
    #        click_button_labeled()
    #        get_alert_feedback()
    #        get_status_feedback()
    #    """
        # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
        # get silva content
    #    data = sb.get_content_data()
    #    self.assertEquals(len(data), 1)
    #    self.assertEquals(data[0]['name'], u'Welcome to Silva!')
    #    content_id = data[0]['id']
    #    sb.select_content(content_id)
    #    status, url = sb.click_button_labeled('delete')
        # test alert msg
    #    self.failUnless(sb.get_alert_feedback().startswith('Could not delete'))
    #    sb.select_content(content_id)
    #    status, url = sb.click_button_labeled('close')
        # test status msg
    #    self.failUnless(sb.get_status_feedback().startswith('Closed'))
        # delete content
    #    sb.select_content(content_id)
    #    status, url = sb.click_button_labeled('delete')
    #    self.failUnless(sb.get_status_feedback().startswith('Deleted'))
        # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)
    
    def test_get_all_content(self):
        """
            test
            get_addables_list()
            select_addable()
            get_addform_title()
            set_id_field()
            set_title_field()
            get_content_data()
            select_all_content
        """
    #    # login
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        # make some content
        # select meta_type
        addables = sb.get_addables_list()
        self.failUnless('Silva Document' in addables)
        sb.select_addable('Silva Document')
        # create silva document
        status, url = sb.click_button_labeled('new...')
        self.failUnless(sb.get_addform_title() == 'create Silva Document')
        # fill in form fields
        sb.set_id_field('test_content')
        sb.set_title_field('test content')
        status, url = sb.click_button_labeled('save')
        self.failUnless(sb.get_status_feedback().startswith('Added Silva Document'))
        # select meta_type
        addables = sb.get_addables_list()
        self.failUnless('Silva Document' in addables)
        sb.select_addable('Silva Document')
        # create silva document
        status, url = sb.click_button_labeled('new...')
        self.failUnless(sb.get_addform_title() == 'create Silva Document')
        # fill in form fields
        sb.set_id_field('test_content2')
        sb.set_title_field('test content2')
        status, url = sb.click_button_labeled('save')
        self.failUnless(sb.get_status_feedback().startswith('Added Silva Document'))
        # get all silva content
        data = sb.get_content_data()
        sb.select_all_content(data)
        # close published content
        status, url = sb.click_button_labeled('close')
        self.failUnless(sb.get_status_feedback().startswith('Closed'))
        data = sb.get_content_data()
        sb.select_all_content(data)
        # delete content
        status, url = sb.click_button_labeled('delete')
        self.failUnless(sb.get_status_feedback().startswith('Deleted'))
        # logout
        status, url = sb.click_href_labeled('logout Manager manager')
        self.assertEquals(status, 401)

    # test field filling methods
    #def test_make_silva_document(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # select meta_type
    #    addables = sb.get_addables_list()
    #    self.failUnless('Silva Document' in addables)
    #    sb.select_addable('Silva Document')
    #    # create silva document
    #    status, url = sb.click_button_labeled('new...')
    #    self.failUnless(sb.get_addform_title() == 'create Silva Document')
    #    # fill in form fields
    #    sb.set_id_field('test_content', 'test content')
    #    sb.set_title_field('test content')
    #    status, url = sb.click_button_labeled('save')
    #    self.failUnless(sb.get_status_feedback().startswith('Added Silva Document'))
    #    # delete content
    #    data = sb.get_content_data()
    #    # get the right content
    #    self.assertEquals(data[1]['name'], u'test content')
    #    sb.select_content('test_content')
    #    status, url = sb.click_button_labeled('delete')
    #    self.failIf('test content' in sb.get_content_ids())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)

    def test_make_silva_folder(self):
        # login
        sb = SilvaBrowser()
        #status, url = sb.login(sb.smi_url(self.silva_url), 'manager', 'secret')
        status, url = sb.login('manager', 'secret', sb.smi_url())
        # select meta_type
        addables = sb.get_addables_list()
        self.failUnless('Silva Folder' in addables)
        sb.select_addable('Silva Folder')
        # create silva folder
        status, url = sb.click_button_labeled('new...')
        self.failUnless(sb.get_addform_title)
        self.failUnless(sb.get_addform_title() == 'create Silva Folder')
        # fill in form fields
        sb.set_id_field('test_content')
        sb.set_title_field('test content')
        sb.set_policy_field('Silva Document')
        status, url = sb.click_button_labeled('save')
        self.failUnless(sb.get_status_feedback().startswith('Added Silva Folder'))
        # delete content
        data = sb.get_content_data()
        # get the right content
        self.assertEquals(data[1]['name'], u'test content')
        sb.select_content('test_content')
        status, url = sb.click_button_labeled('delete')
        self.failIf('test_content' in sb.get_content_ids())
        # logout
        status, url = sb.click_href_labeled('logout Manager manager')
        self.assertEquals(status, 401)

    #def test_make_silva_publication(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # select meta_type
    #    addables = sb.get_addables_list()
    #    self.failUnless('Silva Publication' in addables)
    #    sb.select_addable('Silva Publication')
    #    # create silva publication
    #    status, url = sb.click_button_labeled('new...')
    #    self.failUnless(sb.get_addform_title)
    #    self.failUnless(sb.get_addform_title() == 'create Silva Publication')
    #    # fill in form fields
    #    sb.set_field(id='test_content', title='test content', policy='Silva Document')
    #    status, url = sb.click_button_labeled('save')
    #    self.failUnless(sb.get_status_feedback().startswith('Added Silva Publication'))
    #    # delete content
    #    data = sb.get_content_data()
    #    # get the right content
    #    self.assertEquals(data[1]['name'], u'test content')
    #    sb.select_content('test_content')
    #    status, url = sb.click_button_labeled('delete')
    #    self.failIf('test_content' in sb.get_content_ids())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)

    #def test_make_silva_image(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # select meta_type
    #    addables = sb.get_addables_list()
    #    self.failUnless('Silva Image' in addables)
    #    sb.select_addable('Silva Image')
    #    # create silva publication
    #    status, url = sb.click_button_labeled('new...')
    #    self.failUnless(sb.get_addform_title)
    #    self.failUnless(sb.get_addform_title() == 'upload Silva Image')
    #    # fill in form fields
    #    sb.set_id_title_image_fields('test_content', 'test content')
    #    status, url = sb.click_button_labeled('save')
    #    self.failUnless(sb.get_status_feedback().startswith('Added Silva Image'))
    #    # delete content
    #    data = sb.get_content_data()
    #    self.assertEquals(data[1]['name'], u'test content')
    #    # get the right content
    #    self.assertEquals(data[1]['name'], u'test content')
    #    sb.select_content('test_content')
    #    status, url = sb.click_button_labeled('delete')
    #    self.failIf('test content' in sb.get_content_ids())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)
    
    #def test_make_silva_file(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # select meta_type
    #    addables = sb.get_addables_list()
    #    self.failUnless('Silva File' in addables)
    #    sb.select_addable('Silva File')
    #    # create silva publication
    #    status, url = sb.click_button_labeled('new...')
    #    self.failUnless(sb.get_addform_title)
    #    self.failUnless(sb.get_addform_title() == 'upload Silva File')
    #    # fill in form fields
    #    sb.set_id_title_file_fields('test_content', 'test content')
    #    status, url = sb.click_button_labeled('save')
    #    self.failUnless(sb.get_status_feedback().startswith('Added Silva File'))
    #    # delete content
    #    data = sb.get_content_data()
    #    self.assertEquals(data[1]['name'], u'test content')
    #    # get the right content
    #    self.assertEquals(data[1]['name'], u'test content')
    #    sb.select_content('test_content')
    #    status, url = sb.click_button_labeled('delete')
    #    self.failIf('test content' in sb.get_content_ids())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)
    
    #def test_make_silva_find(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # select meta_type
    #    addables = sb.get_addables_list()
    #    self.failUnless('Silva Find' in addables)
    #    sb.select_addable('Silva Find')
    #    # create silva publication
    #    status, url = sb.click_button_labeled('new...')
    #    self.failUnless(sb.get_addform_title)
    #    self.failUnless(sb.get_addform_title() == 'create Silva Find')
    #    # fill in form fields
    #    sb.set_id_title_fields('test_content', 'test content')
    #    status, url = sb.click_button_labeled('save')
    #    self.failUnless(sb.get_status_feedback().startswith('Added Silva Find'))
    #    # delete content
    #    data = sb.get_content_data()
    #    self.assertEquals(data[1]['name'], u'test content')
    #    # get the right content
    #    self.assertEquals(data[1]['name'], u'test content')
    #    sb.select_content('test_content')
    #    status, url = sb.click_button_labeled('delete')
    #    self.failIf('test content' in sb.get_content_ids())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)
    
    #def test_make_silva_ghost(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('chiefeditor', 'secret', sb.smi_url())
    #    #print sb.browser.contents
    #    # logout
    #    status, url = sb.click_href_labeled('logout ChiefEditor chiefeditor')
    #    self.assertEquals(status, 401)
    #
    #def test_make_silva_ghost_folder(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)
    #
    #def test_make_silva_link(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)
    #
    #def test_make_silva_indexer(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
    #    # logout
    #    status, url = sb.click_href_labeled('logout Manager manager')
    #    self.assertEquals(status, 401)
    #
    #def test_make_silva_link(self):
    #    # login
    #    sb = SilvaBrowser()
    #    status, url = sb.login('manager', 'secret', sb.smi_url())
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaBrowserTest))
    return suite
