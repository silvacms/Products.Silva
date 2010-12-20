##parameters=content=None, category=''
from Products.SilvaMetadata.Exceptions import BindingError

# Build a dict for use in the public pagetemplate,
# format:
# {
#  'setNames': [name1, name2,..],
#   set1: {'setTitle':...,
#          'elementNames': [name1, name2,...],
#           element1: value},
#           element2:...
#         },
#   set2:...
# }

request = context.REQUEST
if content is None:
    content = context.get_viewable()

if content is None:
    return None

ms = context.service_metadata

try:
    binding = ms.getMetadata(content)
except BindingError, be:
    # No binding found..
    return None

renderView = binding.renderElementView
isViewable = binding.isViewable
value = binding.get

pt_binding = {}
pt_binding['setNames'] = set_names = binding.getSetNames(category=category)

for set_name in set_names:
    pt_binding[set_name] = set = {}
    set['setTitle'] = binding.getSet(set_name).getTitle() or set_name
    # Filter for viewable items
    set['elementNames'] = element_names = binding.getElementNames(
        set_name, mode='view')
    # Per element:
    for element_name in element_names:
        # value of element if viewable
        if isViewable(set_name, element_name):
            set[element_name] = renderView(set_name, element_name)

return pt_binding