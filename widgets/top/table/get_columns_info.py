## Script (Python) "get_columns_info"
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
columns = int(node.getAttribute('columns'))
if node.hasAttribute('column_info'):
    column_info = node.output_convert_html(node.getAttribute('column_info'))
else:
    result = []
    for i in range(columns):
        result.append({'align': 'left', 'width': 1, 'html_width':'%s%%' % (100/columns) })
    request.set('columns_info', result)
    return result

lookup = { 'L':'left', 'C':'center', 'R': 'right' }

result = []
for info in column_info.split():
    result.append({ 'align': lookup[info[0]], 'width': int(info[2:]) })

# too much info, ignore it
if len(result) > columns:
    result = result[:columns]
# not enough info, take average and add to missing columns
elif len(result) < columns:
    total = 0
    for info in result:
        total += info['width']
    average = total / len(result)
    for i in range(columns - len(result)):
        result.append({'align': 'left', 'width': average })

# calculate percentages
total = 0
for info in result:
    total += info['width']
for info in result:
    percentage = int((float(info['width'])/total) * 100)
    info['html_width'] = '%s%%' % percentage

# so rows can get it without going through this rigamole again..
request.set('columns_info', result)
return result
