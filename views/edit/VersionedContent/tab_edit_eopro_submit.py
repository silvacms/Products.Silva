## Script (Python) "tab_edit_eopro_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=encoding='latin1'
##title=
##
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
       except Exception,error:
           pass
if error:
    return """
<script type="text/javascript">
window.parent.handleError("ServerError: %s");
</script>
""" % str(error).replace('"', '\\"')

return """
<script type="text/javascript">
  window.parent.handleResponse('%s successfully saved');
</script>
""" % str(model.id)
