from Interface import Base

class ISidebarService(Base):
    def render(obj, tab_name):
        """Returns the rendered PT

        Checks whether the PT is already available cached, if so
        renders the tab_name into it and returns it, if not renders
        the full pagetemplate and stores that in the cache
        """

    def invalidate(obj):
        """Invalidate the cache for a specific object
        """
