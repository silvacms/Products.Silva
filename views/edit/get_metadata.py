##parameters=content
from Products.SilvaMetadata.Exceptions import BindingError

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

renderEdit = binding.renderElementEdit
renderView = binding.renderElementView

aquired_items = binding.listAcquired()
def isAcquired(set_name, element_name):
    if (set_name, element_name) in aquired_items:
        return 1
    return 0

isViewable = binding.isViewable
isEditable = binding.isEditable

pt_binding = {}
pt_binding['setNames'] = set_names = binding.getSetNames()

for set_name in set_names:
    pt_binding[set_name] = set = {}
    set['setTitle'] = binding.getSet(set_name).getTitle() or set_name
    # Filter for viewable items
    set['elementNames'] = element_names = binding.getElementNames(
        set_name, mode='view')
        
    # XXX: hack - this check should go in the element's guard
    if set_name == 'silva-content':
        xtra_editable_check = content.can_set_title()        
    else:
        xtra_editable_check = 1
        
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
        # isEditable, render
        # XXX: using the afformentioned hack...
        if isEditable(set_name, element_name) and xtra_editable_check:
            element['isEditable'] = 1 #isEditable(set_name, element_name)
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

return pt_binding
