# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
from IDataSource import IDataSource

class ISQLDataSource(IDataSource):
    """Access to a SQL data source.
    """

    # ACCESSORS

    def available_connection_ids(self):
        """List ids of available database connections
        """
        pass
        
    # MODIFIERS

    def set_statement(self, statement):
        """SQLDataSources make use of ZSQL Methods. 
        They're supposed to do all the hard work.
        """
        pass

    def set_connection_id(self, id):
        """SQLDataSources make use of ZSQL Methods. 
        They're supposed to do all the hard work.
        """
        pass

