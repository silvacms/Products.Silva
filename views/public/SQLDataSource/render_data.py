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

try:
    data = datasource.get_data(parameters)
except Exception, e:
    return u'<div class="error">[SQL Data Source raises an exception] %s</div>' % e
except:
    # XXX: Ugh, bare except. However the ZSQLMethod seems to raise
    # string type exceptions which I cannot catch here..
    return u'<div class="error">[SQL Data Source is broken]</div>'

# FIXME: Using CSS this hairball is slightly less hairy
# than is used to be
caption = escape_entities(datasource.get_title())
data_encoding = datasource.get_data_encoding()
def ustr(data, enc):
    if data is None:
        return u''
    elif not enc:
        return data
    elif same_type(data, ''):
        return unicode(data, enc, 'replace')
    elif same_type(data, u''):
        return data
    else:
        return unicode(str(data), enc, 'replace')

type = u'listing'
show_headings = u'true'
show_caption = u'true'

table_data = []
if show_headings == 'true':
    table_data.append(u"""<tr class="rowheading">""")
    for name in data.names():
        table_data.append(u"""<td align="%s">\n  %s\n</td>""" % (u'left', ustr(name, data_encoding) ))
    table_data.append(u"""</tr>""")

rownr = 0
for row in data:
    row_data = []
    col = 0
    for field in row:
        # XXX filters out int(0) as well!!
        if field is None:
            field = ''
        elif not same_type(field, '') and not same_type(field, u''):
            field = str(field)
        elif same_type(field, ''):
            field = ustr(field, data_encoding)
        col += 1        
        row_data.append(
            u"""<td align="%s">\n  %s\n</td>""" % (u'left', field))
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
