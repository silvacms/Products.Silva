## Script (Python) "render_data"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=datasource=None
##title=
##
#if not data:
#    return "No resulting data for SQl Data Source &laquo;%s&raquo." % title

data = datasource.get_data()
output_convert = context.output_convert_html

# FIXME: Using CSS this hairball is slightly less hairy
# than is used to be
caption = datasource.get_title_html()
type = 'listing'
show_headings = 'true'
show_caption = 'true'

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
