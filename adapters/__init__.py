# this is a package
import version_management

def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('version_management', 'path')
