##parameters=content, category='', renderFromRequest=False
from Products.SilvaMetadata.Exceptions import BindingError
from Products.Silva.roleinfo import CHIEF_ROLES, READER_ROLES
from Products.Silva.roleinfo import isEqualToOrGreaterThan

# Build a dict for use in the edit pagetemplate,
# format:
# {
#  'setNames': [name1, name2,..],
#   set1: {'elementNames': [name1, name2,...],
#          'setTitle':...,
#           element1: {'view':...,
#                      'isAcquired':...},
#                      'isEditable':...,
#                      'render':...,
#                      'isRequired':...},
#                      'isAcquirable':...},
#                      'description':...},
#                      'title':...},
#           element2:...
#         },
#   set2:...
# }

request = context.REQUEST
model = request.model

if content is None:
    return None

ms = context.service_metadata

try:
    binding = ms.getMetadata(content)
except BindingError, be:
    # No binding found..
    return None
if binding is None:
    return None

user_roles = model.sec_get_all_roles()
def isAllowed(set_name):
    minimal_role = binding.getSet(set_name).getMinimalRole()
    if not minimal_role:
        return True
    for role in user_roles:
        if isEqualToOrGreaterThan(role, minimal_role):
            return True

aquired_items = binding.listAcquired()
def isAcquired(set_name, element_name):
    if (set_name, element_name) in aquired_items:
        return 1
    return 0

def isEditable(set_name, element_name):
    at_least_author = [
        role for role in user_roles if isEqualToOrGreaterThan(role, 'Author')]
    if not at_least_author:
        return False
    # XXX: hack - this check should go in the element's guard
    if set_name == 'silva-content':
        return content.can_set_title()
    return binding.isEditable(set_name, element_name)

renderEdit = binding.renderElementEdit
renderView = binding.renderElementView
isViewable = binding.isViewable

pt_binding = {}
set_names = binding.getSetNames(category=category)
pt_binding['setNames'] = []

for set_name in set_names:
    if not isAllowed(set_name):
        continue # skip this set - it's not allowed
    
    pt_binding['setNames'].append(set_name)
    pt_binding[set_name] = set = {}
    set['setTitle'] = binding.getSet(set_name).getTitle() or set_name
    # Filter for viewable items
    set['elementNames'] = element_names = binding.getElementNames(
        set_name, mode='view')

    # Per element:
    for element_name in element_names:
        set[element_name] = element = {}
        # current value
        element['value'] = binding.get(set_name, element_name)
        # view, maybe acquired
        element['view'] = renderView(set_name, element_name)
        # isAquired
        if isAcquired(set_name, element_name):
            element['isAcquired'] = 1
        else:
            element['isAcquired'] = 0
            
        if isEditable(set_name, element_name):
            element['isEditable'] = 1
            if renderFromRequest:
                #this will happen if there was an error saving the SMI
                #metadata form; pass in the request to renderEdit
                #so that the clients input will be used and not the
                #saved metadata
                element['render'] = renderEdit(set_name, element_name, request)
            else:
                element['render'] = renderEdit(set_name, element_name)
        else:
            # show a field, when it is read-only *and not* acquired (since
            # it then is shown in the acquired content column anyway).
            element['isEditable'] = 0
            element['render'] = None
        # isRequired, isAcquirable, description, title
        bound_element = binding.getElement(set_name, element_name)
        element['isAcquireable'] = bound_element.isAcquireable()
        element['isRequired'] = bound_element.isRequired()
        element['description'] = bound_element.Description()
        element['title'] = bound_element.Title()
        element['hidden'] = bool(bound_element.field.get_value('hidden'))

return pt_binding
