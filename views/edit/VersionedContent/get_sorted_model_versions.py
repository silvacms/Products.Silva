## Script (Python) "get_document_versions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
model = request.model

from Products.Silva.adapters import version_management
adapter = version_management.getVersionManagementAdapter(model)

versions = adapter.getVersions(False)

# sort the versions, order approved, unapproved, published, closed
def sort_versions(a, b):
    ast = a.version_status()
    bst = b.version_status()
    order = ['unapproved', 'approved', 'public', 'last_closed', 'closed']
    ret = cmp(order.index(ast), order.index(bst))
    if ret == 0:
        try:
            ret = cmp(int(b.id), int(a.id))
        except ValueError:
            # non-int id(s)
            ret = cmp(b.id, a.id)
    return ret

versions.sort(sort_versions)
return versions
