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
      frames.logframe.document.write("<p>");
      frames.logframe.document.write(msg);
      frames.logframe.document.write("</p>");
      //alert(msg);
    }
    """)

js.append("""
    function handleError(msg) {
      alert(msg);
    }
    """)

js.append("""
    function functSave() {
      mydoc = document.editor.getHTMLData('http://');
      document.myForm.HTMLDATA.value = mydoc;
      document.myForm.submit();
      document.myForm.save.blur();
    }
    """)


#url = container.REQUEST.model.absolute_url()+'/editor_storage'

js.append("""
    function editorloaded(applet) {
        //applet.insertHTMLData("","hello"); 
        //document.editor.setHTMLData("","startup")
        document.editor.setHTMLData("", document.myForm.HTMLDATA.value); 
        //http://localhost/silva1/test/editor_storage");
        //alert("onEditorLoaded finished");
    }
    """) 
        #//mydoc = document.LastDocumentFrame.document.value;
        #//document.myForm.HTML_DATA_LAST.value=mydoc;

js.append("""
    function functReset() {
      window.location.reload();
      //mydoc = document.myForm.HTMLDATA.value;
    }
    """ )

js.append("""
    function functReload() {
      //document.editor.setHTMLData("http://localhost/silva1/test2/editor_storage");
      document.editor.setHTMLData("", document.myForm.HTMLDATA.value); 
      //document.editor.insertHTMLData("","<h2>title</h2>");
      document.myForm.reload.blur();
      //mydoc = document.myForm.HTMLDATA.value;
    }
    """ )

#from Products.PythonScripts.standard import html_quote

js = map(lambda x: x.strip(), js)

return "\n".join(js)

