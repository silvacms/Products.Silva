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
datasource = context.get_datasource()
parameters = context.get_parameters()

if not datasource:
    return "<span class='warning'>[externaldata element broken]</span>"

data = datasource.get_data(parameters)
output_convert = context.output_convert_html

# FIXME: Using CSS this hairball is slightly less hairy
# than is used to be
caption = datasource.get_title_html()
type = node.getAttribute('type') or 'listing'
show_headings = node.getAttribute('show_headings') or 'true'
show_caption = node.getAttribute('show_caption') or 'true'

table_data = []
if show_headings == 'true':
    table_data.append("""<tr class="rowheading">""")
    for name in data.names():
        table_data.append("""<td align="%s">\n  %s\n</td>""" % ('left', name))
    table_data.append("""</tr>""")

for row in data:
    row_data = []
    col = 0
    for field in row:
        row_data.append(
            """<td align="%s">\n  %s\n</td>""" % ('left', field))
        col += 1
    table_data.append(
        """<tr>\n%s\n</tr>""" % '\n'.join(row_data))

table = []
table.append("""<table class="silvatable %s" width="100%%" cellspacing="0" cellpadding="3px">""" % (type))
if show_caption == 'true':
    table.append("""<caption>%s</caption>""" % (caption))
table.append("""<tbody>""")
table.append('\n'.join(table_data))
table.append("""</tbody>""")
table.append("""</table>""")

return '\n'.join(table) + '\n'
