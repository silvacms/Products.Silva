/* a set of helper functions that should be available on all edit pages */

// can be attached to formfields so that pressing enter makes the form use
// a specific action, useful in forms with more than 1 submit button
function handle_default_action(element, event, action)
{
    code = event.which ? event.which : event.keyCode;
    if (code == 10 || code == 13)
    {
        element.form.action = action;
        element.form.submit();
    }
}

/* this is an event helper function for container 'contents' screens.  
   It should be added to the 'new...' button and the select meta type 
   drop down to enable a 'power user' feature that will place the new 
   content at the position the first item is checked. 
   The add new content functionality should work without using this
   function. */
function addNewContent(event) {
  /* NOTE": the position is "off by one" if the container has an index item.
     So, subtract one when determining the position, if an index document
     is present */
  var idcheckboxes = this.form['ids:list'];
  /* this will be blank if there are no items in the container */
  if (idcheckboxes) {
    var checkboxListHasIndex = (idcheckboxes[0].id == 'index') ? true : false;
    for (var i=0; i < idcheckboxes.length; i++) {
      if (idcheckboxes[i].checked) {
        /* if the index item is checked, leave the position at zero, so the
           new item will be added at position one (as listed in the contents tab)
        */
        if (checkboxListHasIndex && i>0) i-=1;
	this.form['add_object_position'].value = i;
        break;
      };
    };
  };
  return true;
};
