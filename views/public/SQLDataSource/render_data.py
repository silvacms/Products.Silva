from Products.Silva.helpers import escape_entities

request = context.REQUEST
datasource = request.model
title = datasource.get_title_or_id_editable()
parameters = {}

p = datasource.parameters()
if p:
    for name, (type, default, description) in p.items():
        if not default:
            return "SQL Data Source &#xab;%s&#xbb; needs parameter &#xab;%s&#xbb; to have a default value." % (title, name)
        parameters[name] = default

data = datasource.get_data(parameters)

# FIXME: Using CSS this hairball is slightly less hairy
# than is used to be
caption = escape_entities(datasource.get_title())
data_encoding = datasource.get_data_encoding()
type = u'listing'
show_headings = u'true'
show_caption = u'true'

table_data = []
if show_headings == 'true':
    table_data.append(u"""<tr class="rowheading">""")
    for name in data.names():
        table_data.append(u"""<td align="%s">\n  %s\n</td>""" % (u'left', unicode(name, data_encoding, 'replace') ))
    table_data.append(u"""</tr>""")

rownr = 0
for row in data:
    row_data = []
    col = 0
    for field in row:
        col += 1
        row_data.append(
            u"""<td align="%s">\n  %s\n</td>""" % (u'left', unicode(field, data_encoding, 'replace') ))
    rownr += 1
    if rownr % 2: cssclass = u"odd"
    else: cssclass = u"even"
    table_data.append(
        u"""<tr class="%s">\n%s\n</tr>""" % (cssclass, u'\n'.join(row_data)))

table = []
table.append(u"""<table class="silvatable %s" width="100%%" cellspacing="0" cellpadding="3px">""" % (type))
if show_caption == 'true':
    table.append(u"""<caption>%s</caption>""" % (caption))
table.append(u"""<tbody>""")
table.append(u'\n'.join(table_data))
table.append(u"""</tbody>""")
table.append(u"""</table>""")

return (u'\n'.join(table) + u'\n')
