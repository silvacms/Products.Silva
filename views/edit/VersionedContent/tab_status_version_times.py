## Script (Python) "tab_status_version_times"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=version
##title=Revoke approval of approved content
##
view = context
request = view.REQUEST
model = request.model

from Products.Silva.adapters.version_management import \
                            getVersionManagementAdapter
from Products.Silva import mangle

adapter = getVersionManagementAdapter(model)

metadata = view.get_metadata(version)
modificationtime = mangle.DateTime(
        metadata['silva-extra']['modificationtime']['value']
    ).toStr()

# XXX obviously this is dog-slow, could use some optimization...
publicationtime = mangle.DateTime(
        adapter.getVersionPublicationTime(version.id)
    ).toStr()

expirationtime = mangle.DateTime(
        adapter.getVersionExpirationTime(version.id)
    ).toStr()

return modificationtime, publicationtime, expirationtime
