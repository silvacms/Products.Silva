import re
import mimetypes
from urllib2 import HTTPError
from xml.dom import minidom

from Products.Five.testbrowser import Browser

class SilvaBrowser(object):
    def __init__(self):
        self.browser = Browser()

    def click_button_labeled(self, value_name):
        "click on a button with a specific label"
        # for some reason the browser object does not expose
        # enough input and form info, however we can reach what
        # we want through the mech_... objects. Since they are not
        # private (no underscore) this is maybe not too bad...

        # get all forms
        button = None
        for form in self.browser.mech_browser.forms():
            for control in form.controls:
                if not control.type in ['button', 'submit']:
                    continue
                if control.value == value_name:
                    # found the button
                    button = control
        assert button != None, 'No button labeled: %s found' % value_name
        # we cannot click this control, we need to get a browser
        # control, since all controls have a name, we can use that to
        # get the real control.
        self.browser.getControl(name=button.name).click()
        return self.get_status_and_url()

    def click_href_labeled(self, value_name):
        """click on a link with a specific label""" 
        if 'logout' in value_name:
            # logout always results in a 401 error, login window. since
            # you can't access the popup, i accept that a logout is, an href 
            # value_name that has logout in it, and clicking the link there is
            # a 401 HTTPError
            try:
                self.browser.getLink(value_name).click()
            except HTTPError, err:
                if err.code == 401:
                    return self.get_status_and_url()
        else:
            self.browser.getLink(value_name).click()
            return self.get_status_and_url()

    def click_tab_name(self, name):
        "click on a tab"
        url += self.get_url() + '/tab_%s' % name
        self.goto_url(url)

    def get_addables_list(self):
        """return a list of addable meta_type"""
        addables = self.browser.getControl(name='meta_type').options
        addables.remove('None')
        return addables

    def get_addform_title(self):
        "Return a normalized <h2> title for add forms"
        start = self.browser.contents.find('<h2>')
        if start == -1:
            return ''
        end = self.browser.contents.find('</h2>', start)
        return self.html2text(self.browser.contents[start:end+5])

    def get_alert_feedback(self):
        "return the alert message in the page, or an empty string"
        div = '<div class="fixed-alert">'
        start = self.browser.contents.find(div)
        if start == -1:
            return ''
        start += len(div)
        end = self.browser.contents.find('</div>', start)
        return self.browser.contents[start:end].strip()

    def get_content_data(self):
        "return a list of dictionaries decribing the content objects"

        doc = minidom.parseString(self.browser.contents)
        result = []
        for form in doc.getElementsByTagName('form'):
            if form.getAttribute('name') == 'silvaObjects':
                for tbody in form.getElementsByTagName('tbody'):
                    for row in tbody.getElementsByTagName('tr')[1:]:
                        count = 1
                        data = {}
                        for cell in row.getElementsByTagName('td'):
                            if count == 1:
                                data['id'] = cell.getElementsByTagName('input')[0].getAttribute('id')
                            elif count == 2:
                                anchor = cell.getElementsByTagName('a')[-1]
                                data['url'] = anchor.getAttribute('href')
                            elif count == 3:
                                anchor = cell.getElementsByTagName('a')[-1]
                                data['name'] = anchor.childNodes[0].nodeValue
                                css = anchor.getAttribute('class')
                                if css == 'published':
                                    data['closed'] = False
                                    data['published'] = True
                                    data['publishable'] = True
                                elif css == 'draft':
                                    data['closed'] = True
                                    data['published'] = False
                                    data['publishable'] = True
                                else:
                                    data['closed'] = True
                                    data['publishable'] = False
                            elif count == 5:
                                anchor = cell.getElementsByTagName('a')[-1]
                                data['author'] = anchor.childNodes[0].nodeValue
                            count +=1
                        result.append(data)
        return result

    def get_content_ids(self):
        "Get a list of ids for objects in this container"
        return [o['id'] for o in self.get_content_data()]

    def get_status_and_url(self):
        status = self.browser.headers.getheader('Status')
        status = int(status.split(' ')[0])
        return (status, self.browser.url)

    def get_status_feedback(self):
        "return the status message in the page, or an empty string"
        div = '<div class="fixed-feedback">'
        start = self.browser.contents.find(div)
        if start == -1:
            return ''
        start += len(div)
        end = self.browser.contents.find('</div>', start)
        return self.browser.contents[start:end].strip()

    def get_url(self):
        return self.browser.url

    def go(self, url):
        """same as browser.open, but handles http exceptions, and returns http 
        status and url tuple"""

        try:
            self.browser.open(url)
        except HTTPError, err:
            # there is no way to read status from browser,
            # so we'll just have to use the error str, ugh
            return (err.code, None)

        # read status code from first http header
        return self.get_status_and_url()

    def html2text(self, htmlstring):
        """return children of an html element, 
        stripping out child elements, and normalizing
        text nodes """
        # here are two solutions to getting the <h2> text from a form for
        # adding a content type. the commented out was part was the first
        # idea, and then it was decided to use regex. but i don't like this
        # regex because it is too breakable
        p = re.compile('(<h2>\n\s+)(<.+/>\n\s+)(\w+\n\s+\w+\s\w+)')
        result = p.findall(htmlstring)
        result = result[0][2]
        result = re.compile('\n\s+').sub(' ', result)

        #doc = minidom.parseString(htmlstring)
        #result = []
        #for node in doc.firstChild.childNodes:
        #    if node.nodeType != 3:
        #        # not a text node
        #        continue
        #    for word in node.nodeValue.split():
        #        word = word.strip()
        #        result.append(word)
        return result

    def login(self, url, username, password):
        """login to the smi """
        # it seems the Browser object gets confused if 401's are
        # raised. Because of this we always use a new Browser 
        # when logginf in

        self.browser = Browser()
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                          username, password))
        self.browser.addHeader('Accept-Language', 'en-US')
        return self.go(url)

    def logout(self, url):
        """logout of the zmi"""
        url = '%s/manage_zmi_logout' % url
        try:
            self.browser.open(url)
        except HTTPError, err:
            return (err.code, None)

    def remove_all_content(self):
        self.goto_url(self.get_root_url())
        contents = self.get_content_ids()
        for id in contents:
            if not self.is_content_close(id):
                self.close_content(id)
            self.remove_content(id)
        pass

    def select_addable(self, meta_type):
        """select a meta_type from the addables list """
        self.browser.getControl(name='meta_type').value = [meta_type]

    def select_all_content(self, data):
        """toggle all content item checkboxes"""
        # Hack way to select all the checkboxes, since this is done
        # with js
        ids = [item['id'] for item in data]
        self.browser.getControl(name='ids:list').value = ids
        
    def select_content(self, content_id):
        """toggle toggle a content item checkbox"""
        self.browser.getControl(name='ids:list').value = [content_id]

    def smi_url(self, url=None):
        """return the smi url of current url, or url parameter if present"""
        # XXX this should be a bit smarter
        url = url or self.get_url()
        assert url != None, 'Cannot go to SMI here, url does not exist'
        if not url.endswith('/edit') and not '/edit/' in url:
            url += '/edit'
        return url

    def zmi_url(self):
        "go to the zmi page for this url"
        pass

    def public_url(self):
        "go to the public page"
        pass

    def get_content_url(self, content_id):
        "Get url for a content id"
        pass

    def get_content_author(self, content_id):
        "Get author of a content id"
        pass

    ### form filling methods, umm, umm, yum ### 
    def set_id_field(self, id):
        self.browser.getControl(name='field_object_id').value = id
        
    def set_title_field(self, title):
        self.browser.getControl(name='field_object_title').value = title

