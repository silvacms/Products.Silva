
class TocSupport:
    """Mixin for Silva Objects to give them TOC Support.
    """
    def manage_afterAdd(self, item, container):
        #self.inheritedAttribute('manage_afterAdd')(self, item, container)
        toc_ids = getattr(container, '_toc_ids', None)
        #print "afterAdd:", toc_ids
        if toc_ids is None:
            return
        if item.id not in toc_ids:
        #    print "afterAdd"
            toc_ids.append(item.id)
            container._toc_ids = toc_ids
        
    def manage_beforeDelete(self, item, container):
        #self.inheritedAttribute('manage_beforeDelete')(self, item, container)
        toc_ids = getattr(container, '_toc_ids', None)
        #print "beforeDelete:", toc_ids
        if toc_ids is None:
            return
        if item.id in toc_ids:
        #    print "beforeDelete"
            toc_ids.remove(item.id)
            container._toc_ids = toc_ids
    
    def get_full_section_number(self):
        """Get a string that is the number of the section we're in (like 3.1.2)
        """
        numbers = []
        section = self
        while section.meta_type != 'XA Root':
            number = section.get_section_number()
            if number is None:
                return None
            numbers.append(number)
            section = section.aq_parent
        numbers.reverse()
        return '.'.join(map(str, numbers))

    def get_section_number(self):
        """Get the number of the current section in the surrounding section.
        Return None if we should not be in the public toc.
        """
        folder = self.aq_parent
        # get all entries in the parent folder that could be part of toc
        ids = folder.objectIds(['XA Folder', 'XA Document'])
        # if we're 'doc' return None
        if self.id == 'doc':
            return None
        # if we're not published, return None
        if not self.is_published():
            return None
        # get the place in that array that we have
        index = ids.index(self.id)
        # now go find the previous entry
        i = index - 1
        while i >= 0:
            number = getattr(folder, ids[i]).get_section_number()
            if number is not None:
                return number + 1
            i -= 1
        else:
            # we are the first entry
            return 1  
