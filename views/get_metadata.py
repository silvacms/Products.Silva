from Products.SilvaMetadata.Exceptions import BindingError

request = context.REQUEST
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
pt_binding['setNames'] = set_names = binding.getSetNames()

# Build a dict for use in the public pagetemplate,
# format:
# {
#  'setNames': [name1, name2,..],
#   set1: {'elementNames': [name1, name2,...],
#           element1: value},
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
        # value of element if viewable
        if isViewable(set_name, element_name):
            set[element_name] = renderView(set_name, element_name)

return pt_binding