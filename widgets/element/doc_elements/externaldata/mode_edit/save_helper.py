## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
node = request.node
current_path = node.getAttribute('path')
new_path = ''
if request.has_key('path'):
    new_path = request['path']

def removeParameterElements(node):
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            if child.nodeName == 'parameter':
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

node.setAttribute('path', new_path)
datasource = context.get_datasource()
datasource_parameters = datasource.parameters()

if current_path == new_path:
    # same datasource path:
    # set parameter data from form.
    form = datasource.parameter_values_as_form({})
    # validate form
    from Products.Formulator.Errors import FormValidationError
    try:
        result = form.validate_all(request)
    except FormValidationError, e:
        err = e.errors[0]
        raise str(err.error_text)
    removeParameterElements(node)
    for name in datasource_parameters.keys():
        child = node.createElement('parameter')
        child.setAttribute('key', name)
        child.setAttribute('value', result[name])
        node.appendChild(child)
else:
    # different datasource path:
    # get parameter defs.
    # throw away old param elements.
    # set new defaults.
    removeParameterElements(node)
    for name, (type, default_value, description) in datasource_parameters.items():
        child = node.createElement('parameter')
        child.setAttribute('key', name)
        child.setAttribute('value', default_value)
        node.appendChild(child)

type = 'listing'
if request.has_key('element_type'):
    type = request['element_type']
node.setAttribute('type', type)

show_headings = 'yes'
if request.has_key('show_headings'):
    show_headings = request['show_headings']
node.setAttribute('show_headings', show_headings)

show_caption = 'yes'
if request.has_key('show_caption'):
    show_caption = request['show_caption']
node.setAttribute('show_caption', show_caption)
