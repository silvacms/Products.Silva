# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
from IAsset import IAsset

class RequiredParameterNotSetError(Exception):
    pass

class IDataSource(IAsset):
    """A base class for data source
    """
    # ACCESSORS

    def parameters(self):
        """Return dictionary of the form 
        {name: (type, default_value, description)} and description of 
        Author settable parameters. Maybe None
        """
        pass

    def get_data_encoding(self):
        """Since the external datasource data encoding is not know
        we need to provide this information here. The view code uses this
        setting to decode the data into unicode.
        """
        pass

    def get_data(self, **kw):
        """Get data from source with parameter values applied. This most 
        probably only called from the DataElement widget. The result 
        will be a ZSQLMethod-like result. 

        Raises RequiredParameterNotSetError is Auhtor didn't specify 
        values for all parameters.
        
        FIXME: Define "ZSQLMEthod like result"?
        PUBLIC
        """
        pass

    # MODIFIERS
    def set_data_encoding(self, encoding):
        """Since the external datasource data encoding is not know
        we need to provide this information here. The view code uses this
        setting to decode the data into unicode.
        """
        pass

    def set_parameter(self, name, type='string', default_value=None, description=''):
        """Set parameter definition.
        """
        pass

    def unset_parameter(self, name):
        """Unset or remove parameter with name
        """
        pass