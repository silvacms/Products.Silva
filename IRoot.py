from IPublication import IPublication

class IRoot(IPublication):
    """An interface supported by Silva root objects.
    """

    def get_root():
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        pass
    
    def add_silva_addable_forbidden(meta_type):
        """Forbid use of meta_type in SMI. The meta_type won't show
        up anymore, including in the publication metadata tab where
        individual items can be disabled for particular publications.
        """

    def clear_silva_addables_forbidden():
        """Clear any forbidden addables. All addables show up in the
        SMI again.
        """
        
    def is_silva_addable_forbidden(meta_type):
        """Returns true if meta_type should not show up in the SMI.
        """
