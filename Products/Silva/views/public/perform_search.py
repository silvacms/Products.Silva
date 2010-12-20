from Products.Formulator.Errors import ValidationError, FormValidationError

request = context.REQUEST
catalog = context.service_catalog
model = request.model

try:
    result = context.search_form.validate_all_to_request(request)
except FormValidationError, e:
    return None

query = {'version_status': 'public',}

title = result.get('maintitle')
if title:
    query['silvamaintitle'] = title

fulltext = result.get('fulltext')
if fulltext:
    query['fulltext'] = fulltext

metatype = result.get('metatypes')
if metatype:
    query['meta_type'] = metatype

subtree = result.get('search_subtree')
if subtree:
    path = model.get_container().getPhysicalPath()
    query['path'] = '/'.join(path)

#raise str(query)
return catalog(query)
