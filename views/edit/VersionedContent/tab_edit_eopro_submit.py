## Script (Python) "tab_edit_eopro_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=encoding='utf-8'
##title=
##
from Products.PythonScripts.standard import html_quote
import DateTime

error = None

try:
  request = container.REQUEST 
  model = request.model
  
except Exception,error:
  pass

else:
  try:
    htmldata = request['HTMLDATA']
  except Exception,error:
    pass
  else:
    try:
        htmldata = unicode(htmldata, encoding).encode('utf8')
    except Exception, error:
       pass
    else:
       try: 
           model.editor_storage(htmldata)

           #node = request.node
           #context.service_editor.invalidateCaches(node,
           #        ['mode_normal', 'mode/_insert', 'mode_done', 
           #         'mode_edit', 'mode_view'])
       except Exception,error:
           pass

if error:
    return """
<script type="text/javascript">
window.parent.handleError("ServerError: %s");
</script>
""" % str(error).replace('"', '\\')

t = DateTime.DateTime("UTC").Time()

style = "width:150;color: #555555;background: #f3f3d9;border: 1;border-width: 0.5;border-style: solid solid solid solid;margin: 0 0 0 0;"

return """
<html>
<head/>
<body>
<div style="%s">Saving OK %s</div>
</body>
</html>""" % (style, t)

##
#<script type="text/javascript">
#  window.parent.handleResponse("%s GMT saved %s");
#</script>
#""" % (t, str(model.id))
