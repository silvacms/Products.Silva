try:
    from Products.SilvaSchema.validate import validate
except ImportError:
    def validate(xml):
        """We have no validate function, so everything is valid."""
        return 1
