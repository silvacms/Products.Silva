## Script (Python) "tab_edit_eopro_js"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##


js = []

js.append("""
    function handleResponse(msg) {
      alert(msg);
    }
    """)

js.append("""
    function functSave() {
      mydoc = document.myEditor.getHTMLData('http://');
      document.myForm.HTMLDATA.value = mydoc;
      document.myForm.submit();
      document.myForm.save.blur();
    }
    """)


#url = container.REQUEST.model.absolute_url()+'/editor_storage'

#js.append("""
#    function onEditorLoaded() {
#        //mydoc = document.LastDocumentFrame.document.value;
#        //document.myForm.HTML_DATA_LAST.value=mydoc;
#        //alert("onEditorLoaded finished");
#    }
#    """) 

js.append("""
    function functReload() {
      window.location.reload();
      //mydoc = document.myForm.HTMLDATA.value;
    }
    """ )
#from Products.PythonScripts.standard import html_quote

js = map(lambda x: x.strip(), js)

return "\n".join(js)

