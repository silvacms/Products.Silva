# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.11.54.1 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from helpers import add_and_edit
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
from Asset import Asset
import SilvaPermissions
# Formulator
from Products.Formulator.Form import BasicForm
from Products.Formulator.StandardFields import StringField, IntegerField

from interfaces import IDataSource

class DataSource(Asset):
    """Silva can connect to external databases
       (such as LDAP, Postgres, MySQL). Assuming a database connection
       already exists in Zope, content from database tables can be
       retrieved and displayed in Silva pages. Parameters can be set
       and SQL queries defined (using ZSQL method techniques). The data
       is rendered on public pages in one of the Silva table styles. A
       DataSource is usually used in conjunction with an External Data
       element in the Silva editor, but could also be used with a Code
       element.
    """

    __implements__ = IDataSource

    meta_type = "Silva Data Source"

    security = ClassSecurityInfo()

    # XXX class attribute to provide backwards compatibility
    _data_encoding = 'ascii'
    
    def __init__(self, id, title):
        DataSource.inheritedAttribute('__init__')(self, id, title)
        self._parameters = {}
        self._data_encoding = 'ascii'
    
    # ACCESSORS
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'parameters')
    def parameters(self):
        return self._parameters

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_data')
    def get_data(self, parameters={}):
        """
        Get data from DataSource with parameter {key:value}
        dictionary as input
        PUBLIC
        """
        pass

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_data_encoding')
    def get_data_encoding(self):
        return self._data_encoding
        
    # MODIFIERS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_data_encoding')
    def set_data_encoding(self, encoding):
        self._data_encoding = encoding

    security.declareProtected(
            SilvaPermissions.ChangeSilvaContent, 'set_parameter')
    def set_parameter(self, name, type='string', default_value='', description=''):
        self._parameters[name] = (type, default_value, description)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'unset_parameter')
    def unset_parameter(self, name):
        if self._parameters.has_key(name):
            del self._parameters[name]

    # UI CONVENIENCE

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'parameter_string_to_dict')
    def parameter_string_to_dict(self, parameter_string):
        """ String format: "type : name [: default value [: description]]"
        """
        parameters = {}
        if not parameter_string:
            return parameters

        if not parameter_string.find('\n'):
            parameter_string = parameter_string.replace('\r', '\n')
        else:
            parameter_string = parameter_string.replace('\r', '')
        parameter_string = parameter_string.split('\n')
        
        for line in parameter_string:
            values = map(lambda s: s.strip(), line.split(':'))
            type = values[0]
            name = values[1]
            default_value = ''
            description = ''
            if len(values) > 2:
                default_value = values[2]
                if len(values) > 3:
                    description = values[3]
            parameters[name] = (type, default_value, description)
        return parameters

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'parameter_as_form')
    def parameter_values_as_form(self, parameters={}):
        """ Parameter format: {name: value}
        """
        form = BasicForm().__of__(self)
        for name, (type, value, description) in self._parameters.items():
            if parameters.has_key(name):
                value = parameters[name]
            field = StringField(
                name, title=name, default=value, 
                description=description, unicode=1).__of__(self)
            # XXX Hack - In noraml forms, get_form_encoding would be found
            # by aqcuisistion...
            field.get_form_encoding = form.get_form_encoding
            form.add_field(field)
        return form


InitializeClass(DataSource)
