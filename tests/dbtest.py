import unittest
import ZODB # for Persistent
import glob
import os
import sys

import unittest

class PersistenceTestCase(unittest.TestCase):
    """Base class to test objects in a ZODB.
    """
    def openDB(self):
        from ZODB.FileStorage import FileStorage
        from ZODB.DB import DB
        storage = FileStorage(self.dbName)
        db = DB(storage)
        self.db = db.open().root()

    def closeDB(self):
        get_transaction().commit()
        self.document = None
        self.db._p_jar._db.close()
        self.db = None

    def cycleDB(self):
        self.closeDB()
        self.openDB()
        # should call some setup here

    def delDB(self):
        map(os.unlink, glob.glob("fs_tmp__*"))

    def setUp(self):
        """open db."""

        self.dbName = 'fs_tmp__%s' % os.getpid()
        self.openDB()
        # should call some action here
        get_transaction().commit()
  
    def tearDown(self):
        self.closeDB()
        self.delDB()

