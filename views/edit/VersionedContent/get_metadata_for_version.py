## Script (Python) "get_metadata_for_version"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=versionid
##title=Revoke approval of approved content
##

# XXX: SHOULD NEVER BE CALLED FROM PUBLIC VIEW CODE, USES
# THE OLD INEFFICIENT METADATA CALL

view = context
request = view.REQUEST
model = request.model

from Products.Silva.adapters.version_management import \
                            getVersionManagementAdapter
adapter = getVersionManagementAdapter(model)
version = adapter.getVersionById(request.version)

return view.service_metadata.getMetadata(version)
