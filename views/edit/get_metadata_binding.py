ms = context.service_metadata
request = context.REQUEST
model = request.model
                             
editable = model.get_editable()
if editable is None:
    # No editable version
    return None

binding = ms.getMetadata(editable)

renderEdit = binding.renderElementEdit
renderView = binding.renderElementView

aquired_items = binding.listAcquired()
def isAcquired(set_name, element_name):
    if (set_name, element_name) in aquired_items:
        return 1
    return 0

isViewable = binding.isViewable
isEditable = binding.isEditable

value = binding.get

pt_binding = {}
pt_binding['setNames'] = set_names = binding.getSetNames()

# Build a dict for use in the pagetemplate,
# format:
# {
#  'setNames': [name1, name2,..],
#   set1: {'elementNames': [name1, name2,...],
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
for set_name in set_names:
    pt_binding[set_name] = set = {}
    # Filter for viewable items
    set['elementNames'] = element_names = binding.getElementNames(
        set_name, mode='view')
    # Per element:
    for element_name in element_names:
        set[element_name] = element = {}
        # view, maybe acquired
        element['view'] = renderView(set_name, element_name)
        # isAquired
        if isAcquired(set_name, element_name):
            element['isAcquired'] = 1
        else:
            element['isAcquired'] = 0        
        # isEditable, render
        if isEditable(set_name, element_name):
            element['isEditable'] = isEditable(set_name, element_name)
            element['render'] = renderEdit(set_name, element_name)
        else:
            # show a field, when it is read-only *and not* acquired
            if not element['isAcquired']:
                element['render'] = element['view']
            else:
                element['render'] = None
        # description, isRequired, isAcquirable
        bound_element = binding.getElement(set_name, element_name)
        element['isAcquireable'] = bound_element.isAcquireable()        
        element['isRequired'] = bound_element.isRequired()
        element['description'] = bound_element.Description()
        element['title'] = bound_element.Title()

return pt_binding