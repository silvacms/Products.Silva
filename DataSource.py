# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from helpers import add_and_edit
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva interfaces
from IDataSource import IDataSource
# Silva
from Asset import Asset
import SilvaPermissions

class DataSource(Asset):
    """A base class for data source
    """

    __implements__ = IDataSource

    meta_type = "Silva Data Source"

    security = ClassSecurityInfo()
    
    def __init__(self, id, title):
        DataSource.inheritedAttribute('__init__')(self, id, title)
        self._parameters = {}
    
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

    # MODIFIERS
    security.declareProtected(
            SilvaPermissions.ChangeSilvaContent, 'set_parameter')
    def set_parameter(self, name, type='string', default_value=None, description=''):
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
            default_value = None
            description = None
            if len(values) > 2:
                default_value = values[2]
                if len(values) > 3:
                    description = values[3]
            parameters[name] = (type, default_value, description)

        return parameters

    
InitializeClass(DataSource)