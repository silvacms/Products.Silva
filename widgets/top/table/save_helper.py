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

node.setAttribute('type', node.input_convert(request['element_type']))

lookup = {'left':'L', 'center':'C', 'right':'R'}

columns = context.get_columns()
# process column info
column_info = []
for column in range(columns):
    key = 'column_align_%s' % column
    if request.has_key(key):
       align = lookup.get(request[key], 'L')
    else:
       align = 'L'
    key = 'column_width_%s' % column
    if request.has_key(key):
       width = request[key]
       try:
         width = int(width)
         if width < 1:
             width = 1
       except ValueError:
         width = 1
    else:
       width = 1
    column_info.append('%s:%s' % (align, width))

node.setAttribute('column_info', node.input_convert(' '.join(column_info)))
