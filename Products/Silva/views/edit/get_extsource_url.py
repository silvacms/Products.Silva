##parameters=id

from Products.SilvaExternalSources.ExternalSource import getSourceForId
source = getSourceForId(context.REQUEST.model, id)
if source is not None:
    return source.absolute_url()
return ''
