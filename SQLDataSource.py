# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.11.48.1 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from helpers import add_and_edit
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# SQLMethods
from Products.ZSQLMethods.SQL import SQLConnectionIDs, SQL
# Silva
from DataSource import DataSource
import SilvaPermissions

from interfaces import ISQLDataSource

icon="www/silvasqldatasource.png"
addable_priority = 1

class SQLDataSource(DataSource):
    __implements__ = ISQLDataSource
    
    meta_type = "Silva SQL Data Source"

    security = ClassSecurityInfo()

    sql_method_id = 'sql_method'

    def __init__(self, id, title):
        SQLDataSource.inheritedAttribute('__init__')(self, id, title)
        self._sql_method = None
        self._statement = None
        self._connection_id = None

    # ACCESSORS
   
    #FIXME: what permissions?
    def connection_id(self):
        return self._connection_id

    #FIXME: what permissions?
    def statement(self):
        return self._statement
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_data')
    def get_data(self, params={}):
        """Silva can connect to external databases
        (such as LDAP, Postgres, MySQL). In conjunction with a database
        connection  in Zope,  content from data base tables can be
        retrieved and displayed in Silva pages.  In the DataSource
        parameters can be set and SQL queries defined (using ZSQL method
        techniques). The data is rendered on public pages in a table.
        """
        if not self._sql_method:
            self._set_sql_method()
        return self._sql_method(REQUEST=params)
    
    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_parameter')
    def set_parameter(self, name, type='string', default_value='', description=''):
        SQLDataSource.inheritedAttribute('set_parameter')(
            self, name, type, default_value, description)
        #invalidate sql method
        self._sql_method = None
        self._p_changed = 1

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'unset_parameter')
    def unset_parameter(self, name):
        SQLDataSource.inheritedAttribute('unset_parameter')(self, name)
        #invalidate sql method
        self._sql_method = None
        self._p_changed = 1

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_statement')
    def set_statement(self, statement):
        self._statement = statement
        #invalidate sql method
        self._sql_method = None
        self._p_changed = 1

    security.declareProtected(
            SilvaPermissions.ChangeSilvaContent, 'set_connection_id')
    def set_connection_id(self, id):
        self._connection_id = id
        #invalidate sql method
        self._sql_method = None
        self._p_changed = 1
        
    def _set_sql_method(self):
        arguments = []
        params = self.parameters()
        if params:
            for name, (type, default_value, description) in params.items():
                arg = '%s:%s' % (name, type)
                if default_value:
                    arg = '%s=%s' % (arg, default_value)
                    arguments.append(arg)
                
        arguments = '\n'.join(arguments)
        self._sql_method = SQL(
            self.sql_method_id, '', self._connection_id, 
            arguments.encode('ascii'), self._statement.encode('ascii'))
        self._p_changed = 1


InitializeClass(SQLDataSource)


from AccessControl import allow_module
allow_module('Products.Silva.SQLDataSource')
#FIXME: what permissions, if at all?
def available_connection_ids(context):
    return SQLConnectionIDs(context)

manage_addSQLDataSourceForm=PageTemplateFile(
    "www/SQLDataSourceAdd", globals(), __name__='manage_addSQLDataSourceForm', 
    Kind='File', kind='file')

def manage_addSQLDataSource(context, id, title, REQUEST=None):
    sql_datasource = SQLDataSource(id, title)
    context._setObject(id, sql_datasource)
    sql_datasource = context._getOb(id)
    sql_datasource.set_title(title)
    add_and_edit(context, id, REQUEST)
    return sql_datasource
