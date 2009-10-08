# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import xmlrpclib
# Zope
import Globals
from AccessControl import Permissions, ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit
from Products.Silva.i18n import translate as _

from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf

class Job(object):
    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, id, format, description):
        self.id = id
        self.format = format
        self.description = description


class DocmaService(SilvaService):

    security = ClassSecurityInfo()
    meta_type = 'Docma Service'

    manage_options = (
                      {'label': 'Edit', 'action': 'edit_tab'},
                      {'label': 'Info', 'action': 'info_tab'}
                      ) + SilvaService.manage_options

    manage_main = edit_tab = PageTemplateFile('www/serviceDocmaEditTab',
                                              globals(), __name__='edit_tab')
    info_tab = PageTemplateFile('www/serviceDocmaInfoTab',
                                globals(), __name__='info_tab')

    for tab in ('manage_main', 'edit_tab', 'info_tab'):
        security.declareProtected('View management screens', tab)

    silvaconf.icon('www/docma.png')
    silvaconf.factory('manage_addDocmaServiceForm')
    silvaconf.factory('manage_addDocmaService')

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._password = 'secret'
        self._host = '0.0.0.0'
        self._port = '8888'
        self._jobpathmappings = {}

    security.declareProtected(Permissions.manage_properties, "set_data")
    def set_data(self, password, host, port):
        """Sets the data"""
        self._password = password
        self._host = host
        self._port = port

    security.declareProtected(Permissions.manage_properties, "host")
    def host(self):
        """Returns the host"""
        return self._host

    security.declareProtected(Permissions.manage_properties, "port")
    def port(self):
        """Returns the port"""
        return self._port

    security.declareProtected(Permissions.manage_properties, "password")
    def password(self):
        """Returns the password"""
        return self._password

    security.declareProtected(Permissions.access_contents_information,
                              "silva2word")
    def silva2word(self, email, xml, fronttemplate, username, description):
        """Silva to Word conversion"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        if fronttemplate.endswith('.doc'):
            fronttemplate = fronttemplate[:-4]
        (ident, storageid) = server.silva2word(
            username, self._password, email, fronttemplate,
            xmlrpclib.Binary(xml), description)
        status = server.getJobStatus(ident)
        return (ident, status)

    security.declareProtected(Permissions.access_contents_information,
                              "word2silva")
    def word2silva(self, wordfile, username, email, description):
        """Word to Silva conversion"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        ident, storageid = server.word2silva(
            username, self._password, xmlrpclib.Binary(wordfile),
            email, '', description)
        status = server.getJobStatus(ident)
        return (ident, status)

    security.declareProtected(Permissions.access_contents_information,
                              "try_connection_and_pw")
    def try_connection_and_pw(self):
        from socket import error
        try:
            server = xmlrpclib.Server(
                "http://%s:%s" % (self._host, self._port))
            correct = server.try_password(self._password)
            if not correct:
                return 0
            return 1
        except error:
            return 0

    security.declareProtected(Permissions.access_contents_information,
                              "get_templates")
    def get_templates(self):
        """Returns the list of available templates from the server."""
        if not self.try_connection_and_pw():
            # XXX i18n - are we sure this is not used for functional purposes?
            return [_('Not connected')]
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        retval = server.getTemplates(self._password)
        if len(retval) == 0:
            return ['']
        return retval

    security.declarePrivate('add_template')
    def add_template(self, filename, filedata):
        """Adds a template to the serverdir.

        This method does NO CHECKING, it's up to the manager to send
        correct data.
        """
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.addTemplate(self._password, filename,
                                  xmlrpclib.Binary(filedata))

    security.declarePrivate('delete_template')
    def delete_template(self, filename):
        """Deletes a template from the server"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.delTemplate(self._password, filename)

    security.declareProtected(Permissions.access_contents_information,
                              'get_index')
    def get_index(self, ident):
        """Returns the index of ident in the (ordered) commandqueue"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.getIdentIndex(ident)

    security.declareProtected(Permissions.access_contents_information,
                              'get_estimated_time_for_type')
    def get_estimated_time_for_type(self, type):
        """Returns the estimated time 1 item takes to process"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return 1

    security.declareProtected(Permissions.access_contents_information,
                              'get_estimated_time_for_ident')
    def get_estimated_time_for_ident(self, ident):
        """Returns the time it will take for a certain process is done"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return int(server.getEstimatedIdentTime(ident))

    security.declareProtected(Permissions.access_contents_information,
                              'get_queue')
    def get_queue(self):
        """Returns a list of queued idents in the order they will be
        processed"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.getIdentQueue()

    security.declareProtected(Permissions.access_contents_information,
                              'get_processing_ident')
    def get_processing_ident(self):
        """Returns the ident of the current processing job"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.getProcessingIdent()

    security.declareProtected(Permissions.access_contents_information,
                              'get_status')
    def get_status(self, ident):
        """Returns the status of ident"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.getJobStatus(ident)

    security.declareProtected(Permissions.access_contents_information,
                              'get_ident_owner')
    def get_ident_owner(self, ident):
        """Returns the owner of ident"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.getIdentOwner(ident)

    security.declareProtected(Permissions.access_contents_information,
                              'get_ident_description')
    def get_ident_description(self, ident):
        """Returns the description of ident"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        return server.getDescription(ident)

    security.declareProtected(Permissions.access_contents_information,
                              'get_finished_jobs_for_userid')
    def get_finished_jobs_for_userid(self, ident, format=None):
        """Returns a list of idents of finished jobs for a certain user"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        retval = server.getResultDescriptionsByUser(ident)
        retval = \
            map(lambda (storage_id, description, format): \
                Job(storage_id, format, description), 
                retval)
        if format is not None:
            retval = filter(lambda job: job.format == format, retval)
        retval.sort(lambda job1, job2: job1.id > job2.id or -1)
        return retval

    security.declareProtected(Permissions.access_contents_information,
                              'get_finished_job')
    def get_finished_job(self, userid, storageid):
        """Returns the XML for a finished job"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        retval = server.getResult(userid, self._password, storageid)
        if isinstance(retval, xmlrpclib.Binary):
            return retval.data
        raise Exception, ('Job %s is not in the queue.'
                          'This job may have been expired.' % storageid)

    security.declareProtected(Permissions.access_contents_information,
                              'delete_finished_job')
    def delete_finished_job(self, userid, storageid):
        """Deletes a finished job from the server"""
        server = xmlrpclib.Server("http://%s:%s" % (self._host, self._port))
        server.delResult(userid, self._password, storageid)

    security.declareProtected(Permissions.manage_properties,
                              'manage_update_settings')
    def manage_update_settings(self, REQUEST):
        """The function called from the edit-form"""
        if (REQUEST.has_key('new_template') and
            hasattr(REQUEST['new_template'], 'filename') and
            REQUEST['new_template'].filename):
            data = REQUEST['new_template'].read()
            filename = REQUEST['new_template'].filename
            self.add_template(filename, data)

        host = REQUEST['host']
        port = REQUEST['port']
        password = REQUEST['password']
        self.set_data(password, host, port)

        return self.edit_tab(manage_tabs_message='Data updated')

    security.declareProtected(Permissions.manage_properties,
                              "manage_delete_template")
    def manage_delete_template(self, REQUEST):
        """Called when a template is chosen for deletion"""
        filename = REQUEST['template']
        res = self.delete_template(filename)

        if res:
            return self.edit_tab(manage_tabs_message='Template deleted')
        else:
            return self.edit_tab(manage_tabs_message='Error deleting template')

Globals.InitializeClass(DocmaService)

manage_addDocmaServiceForm = PageTemplateFile(
        'www/serviceDocmaAdd', globals(),
        __name__ = 'manage_addDocmaServiceForm')

def manage_addDocmaService(self, id, title='', REQUEST=None):
    """Add service to folder
    """
    # add actual object
    id = self._setObject(id, DocmaService(id, title))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''
