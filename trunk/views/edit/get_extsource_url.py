##parameters=id

from Products.SilvaExternalSources.ExternalSource import getSourceForId
return getSourceForId(context.REQUEST.model, id).absolute_url()
