## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
output_convert = context.output_convert_html
columns_info = context.get_columns_info()

# FIXME: This hairball is no less hairy than is used to be
# but at least it now renders EUR style tables
#
# Put table data in a 2-dim. matrix
table_data = []
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'row':
        row_data = []
        for field in child.childNodes:
            if field.nodeType != node.ELEMENT_NODE:
                continue
            if field.nodeName == 'field':
                # get field content
                if context.is_field_simple(field):
                    for p_node in field.childNodes:
                        if p_node.nodeType == node.ELEMENT_NODE:
                            break
                    content = node.render_text_as_html(p_node)
                else:
                    context.service_editor.setViewer('service_sub_previewer')
                    content = context.service_editor.getViewer().getWidget(field).render()
                # append field content
                if content == '':
                    content = '&nbsp;'
                row_data.append(content)
        table_data.append(row_data)
    if child.nodeName == 'row_heading':
        row_data = []
        row_data.append(node.render_heading_as_html(child))
        table_data.append(row_data)

# Table specs
nr_of_columns = len(columns_info)
type = node.getAttribute('type')

# Field render function
FIRST       = 1
CONSECUTIVE = 2
LAST        = 3
def render_fields(fields, cols, seq):
    # If borders required, determine style for this table type
    if type in ['listing', 'grid', 'datagrid']:
        style = ['borders'] # for all but rightmost cells
        style_last = ['borders'] # style_last is exception for rightmost cell
        if type == 'listing' and seq == FIRST:
            style.append('bottom')
            style_last.append('bottom')
        elif type == 'grid':
            style.append('topleft')
            style_last = style_last + ['topleft', 'right']
            if seq == LAST:
                style.append('bottom')
                style_last.append('bottom')
        elif type == 'datagrid' and seq != FIRST:
            style.append('topleft')
            style_last = style_last + ['topleft', 'right']
            if seq == LAST:
                style.append('bottom')
                style_last.append('bottom')
    else:
        style = style_last = []
    
    if seq == FIRST:
        # for cells in the first row
        style.append('column-heading')
        style_last.append('column-heading')

    # Now formulate the actual td tag, with class attribute
    result = []
    if len(fields) == 1:
        # for rows with just 1 cell (a.k.a. row header) we span
        style_last.append('column-spanheading')
        layout = 'colspan="%s"' % nr_of_columns
        result.append('<td %s valign="top" class="%s">%s</td>' % (
            layout, ' '.join(style_last), fields[0]))
    else:
        for i in range(len(fields) - 1):
        # all but last cell
            info = columns_info[i]
            layout = 'valign="top" align="%s" width="%s"' % (
                info['align'], info['html_width'])
            result.append('<td %s class="%s">%s</td>' % (
                layout, ' '.join(style), fields[i]))
        # last cell
        info = columns_info[-1]
        layout = 'valign="top" align="%s" width="%s"' % (
            info['align'], info['html_width'])
        result.append('<td %s class="%s">%s</td>' % (
            layout, ' '.join(style_last), fields[-1]))
    return result

if len(table_data) == 0:
    return "empty table"

# Start rendering table from matrix
rendered_table = []
rendered_table.append('<table width="100%" cellspacing="0" cellpadding="0">')
#first row:
r = FIRST
if len(table_data) == 1: 
    # first row is last, in a 1 row table
    r = LAST 
row = table_data[0]
if row:
    rendered_table.append('<tr>')
    rendered_table = rendered_table + render_fields(row, nr_of_columns, r)
    rendered_table.append('<tr>')
#consecutive, but last, rows:
rows = table_data[1:-1]
for row in rows:
    rendered_table.append('<tr>')
    rendered_table = rendered_table + render_fields(row, nr_of_columns, CONSECUTIVE)
    rendered_table.append('</tr>')
#last row:
if len(table_data) > 1: 
    # but not if last == first row
    row = table_data[-1]
    rendered_table.append('<tr>')
    rendered_table = rendered_table + render_fields(row, nr_of_columns, LAST)
    rendered_table.append('</tr>')
rendered_table.append('</table>')

return '\n'.join(rendered_table) + '\n'
