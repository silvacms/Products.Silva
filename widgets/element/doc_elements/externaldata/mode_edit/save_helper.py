from Products.Formulator.Errors import FormValidationError, ValidationError

request = context.REQUEST
node = request.node
session = request.SESSION

current_path = node.getAttribute('path')
new_path = ''
if request.has_key('path'):
    new_path = request['path']

def removeParameterElements(node):
    removeChilds = [child for child in node.childNodes if 
                       child.nodeType == node.ELEMENT_NODE and 
                           child.nodeName == 'parameter']
    for child in removeChilds:
        try:
            node.removeChild(child)
        except ValueError:
            pass

if not new_path:
    # no path set.
    # get rid of parameters(?)
    # return.
    node.removeAttribute('path')
    removeParameterElements(node)
    return

node.setAttribute('path', node.input_convert(new_path))
datasource = context.get_datasource()
datasource_parameters = datasource.parameters()

if current_path == new_path:
    # same datasource path:
    removeParameterElements(node)
    
    # validate form
    errors = {}
    form = datasource.parameter_values_as_form()
    for field in form.get_fields():
        try:
            value = field.validate(request)
        except ValidationError, e:
            errors[e.field_id] = e.error_text
        else:
            # Set parameter data from form. Form outputs unicode!
            child = node.createElement('parameter')
            child.setAttribute('key', field.id)
            child.setAttribute('value', value)
            node.appendChild(child)
else:
    # different datasource path:
    removeParameterElements(node)
    for name, (type, default_value, description) in datasource_parameters.items():
        # get parameter defs.
        # throw away old param elements.
        # set new defaults.
        # Form outputs unicode!
        child = node.createElement('parameter')
        child.setAttribute('key', name)
        child.setAttribute('value', default_value)
        node.appendChild(child)

type = 'list'
if request.has_key('element_type'):
    type = request['element_type']
node.setAttribute('type', node.input_convert(type))

show_headings = 'true'
if request.has_key('show_headings'):
    show_headings = request['show_headings']
node.setAttribute('show_headings', node.input_convert(show_headings))

show_caption = 'true'
if request.has_key('show_caption'):
    show_caption = request['show_caption']
node.setAttribute('show_caption', node.input_convert(show_caption))
