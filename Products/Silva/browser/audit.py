from Products.Five import BrowserView

class CatalogObjectAudit(BrowserView):
    """This is a helper view (on Silva Root) to clean out service_catalog.
       As time passes objects can be removed from the catalog without
       cleaning up their rids -- so remnants of the object are still in the
       catalog (e.g. either in the metadata, in the paths or uids.  This can
       lead to POSKey errors when traversing result sets."""
    def __init__(self, context, request):
        super(CatalogObjectAudit, self).__init__(context, request)
        self.sc = self.context.service_catalog
        self.sc_ = self.sc._catalog
        self.output = []
    def _cleanup_catalog_datastructures(self):
        """look in data, uids and paths to find any inconsistencies"""
        for k in self.sc_.data: #key=rid, data=metadata
            if k not in self.sc_.paths:
                self.output.append('METADATA RID: %s not in PATHS, removing from DATA'%(k))
                #del self.sc_.data[k]
        for rid in self.sc_.paths:
            if rid not in self.sc_.data: #no metadata exists for rid
                self.output.append('PATHS RID: %s not in DATA, removing from PATHS'%(rid))
                #del self.sc_.paths[rid]
        for (uid,rid) in self.sc_.uids.items(): #uids maps a uid(physicalpath) to an rid
            if rid not in self.sc_.paths:
                #del self.sc_.uids[uid]
                if rid in self.sc_.data:
                    self.output.append('UIDS UID: %s not in PATHS[%s] but in DATA, removing from UIDS and DATA'%(uid,rid))
                    #del self.sc_.data[rid]
                else:
                    self.output.append('UIDS UID: %s not in PATHS[%s] and not in DATA, removing from UIDS'%(uid,rid))
            elif rid not in self.sc_.data:
                #del self.sc_.uids[uid]
                if rid in self.sc_.paths:
                    self.output.append('UIDS UID: %s not in DATA[%s] but in PATHS, removing from UIDS and PATHS'%(uid,rid))
                    #del self.sc_.paths[rid]
                else:
                    self.output.append('UIDS UID: %s not in PATHS[%s] and not in DATA, removing from UIDS'%(uid,rid))  

    def _cleanup_indexes(self):
        for i in self.sc.getIndexObjects():
            self._cleanup_index(i)

    def _cleanup_index(self, index):
        #only if it has _unindex
        if not hasattr(index.aq_explicit, 'documentToKeyMap'):
            self.output.append("SKIPPING INDEX %s  (no documentToKeyMap)"%index.id)
            return
        #loop through unindex, seeing if each index is in self.sc_.paths
        self.output.append("CHECKING %s"%(index.id))
        for rid in index.documentToKeyMap().keys():
            if rid not in self.sc_.paths:
                self.output.append("%s KEY NOT FOUND IN PATHS, REMOVING FROM INDEX"%rid)
                index.unindex_object(rid)

    def __call__(self):
        sc = self.sc
        sc_ = self.sc._catalog
        self.request.RESPONSE.setHeader('content-type','text/plain')
        self.output.append("CLEANING UP CATALOG DATASTRUCTURES")
        self.output.append("----------------------------------")
        #self._cleanup_catalog_datastructures()
        self.output.append("CLEANING UP INDEXES")
        self.output.append("----------------------------------")
        self._cleanup_indexes()
        self.output.append('----')
        self.output.append('DONE')
        return '\n'.join(self.output)
