from IContainer import IContainer

class IPublication(IContainer):
    """An interface supported by publication objects.
    """
    def set_silva_addables_allowed_in_publication(addables):
        """Set the list of addables explicitly allowed in this publication.
        If 'addables' is set to None the list is acquired from the
        publication higher in the hierarchy. If this is the root,
        return the complete list.
        """
    
    def get_silva_addables_allowed_in_publication():
        """Get a list of all addables explicitly allowed in this
        publication (and its subcontainers).
        """

    def is_silva_addables_acquired():
        """Return true if the list of addables is acquired from
        above (set_silva_addables_allowed_in_publication set to None), false
        if not.
        """
