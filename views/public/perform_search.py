from Products.Silva.helpers import escape_entities
from Products.Formulator.Errors import ValidationError, FormValidationError

request = context.REQUEST
catalog = context.service_catalog
model = request.model
view = context

try:
    result = view.search_form.validate_all_to_request(request)
except FormValidationError, e:
    return None

query = {'version_status': 'public',}

if hasattr(result, 'maintitle'):
    query['silvamaintitle'] = result['maintitle']

if hasattr(result, 'fulltext'):
    query['fulltext'] = result['fulltext']

return catalog(query)
