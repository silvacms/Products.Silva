/* a set of helper functions that should be available on all edit pages */

// can be attached to formfields so that pressing enter makes the form use
// a specific action, useful in forms with more than 1 submit button
handle_default_action = function(element, event, action)
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
addNewContent = function(event) {
  /* NOTE": the position is "off by one" if the container has an index item.
     So, subtract one when determining the position, if an index document
     is present */
  var idcheckboxes = this.form['ids:list'];
  /* this will be blank if there are no items in the container */
  if (idcheckboxes) {
    if (idcheckboxes.length==null && 
	    idcheckboxes.id != 'index') {
      if (idcheckboxes.checked) {/* there is only a single checkbox, 
                                    on the page, it isn't the
                                    index document, and it is checked */
        this.form['add_object_position'].value = 0;
      };
    } else {
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
  };
  return true;
};

/* helper for the lookup window widgets, to add an additional
   row for placing a reference */
addRowToReferenceLookupWidget = function(input,maxrows) {
  var tbody = input;
  while (tbody.nodeName != 'TBODY') tbody = tbody.parentNode;
  var trs = -1; /* start at -1, since one row is the add buttonr ow */
  for (var n=0; n < tbody.childNodes.length; n++) {
    if (tbody.childNodes[n].tagName == 'TR')
      trs++;      
  };
  if (trs == maxrows) {
    alert("Unable to add additional reference.  The number of references allowed for this field is " + maxrows);
    return;
  };
  var copy = tbody.lastChild.previousSibling.cloneNode(true);
  var key = input.getAttribute('id').replace(/^addbutton_/,'');
  var refinput = copy.getElementsByTagName('input')[0]; /* this is the ref text field*/
  var index = parseInt(refinput.id.replace(/^input(\d*)_.*$/,'$1')) + 1;
  refinput.value = '';
  refinput.id = 'input' + index + '_' + key;
  refinput.setAttribute('taid', 'inputta' + index + '_' + key);
 
  var ta = copy.getElementsByTagName('textarea')[0];
  ta.id = 'inputta' + index + '_' + key;
  ta.setAttribute('key', refinput.id);
  ta.name = ta.id;
  var buttons = copy.getElementsByTagName('button');
  var lbutton = buttons[0];
  var editbutton = null;
  var removebutton = null;
  if (buttons.length == 3) { // both edit and remove buttons
    editbutton = buttons[1];
    removebutton = buttons[2];
  } else if (buttons.length == 2) {
    if (buttons[1].name.search(/editbutton/)>-1) {
      editbutton = buttons[1];
    } else {
      removebutton = buttons[1];
    };
  };

  var keyrepl = new RegExp("(.*?)\\d*(_" + key + ")$", 'g');
  lbutton.setAttribute('id',lbutton.getAttribute('id').replace(keyrepl,"$1"+index+"$2"));
  lbutton.setAttribute('name',lbutton.getAttribute('name').replace(keyrepl,"$1"+index+"$2"));
  if (editbutton) {
    editbutton.style.display = 'none';
    editbutton.setAttribute('id',editbutton.getAttribute('id').replace(keyrepl,"$1"+index+"$2"));
    editbutton.setAttribute('name',editbutton.getAttribute('name').replace(keyrepl,"$1"+index+"$2"));
  };
  if (removebutton) {
    removebutton.setAttribute('id',removebutton.getAttribute('id').replace(keyrepl,"$1"+index+"$2"));
    removebutton.setAttribute('name',removebutton.getAttribute('name').replace(keyrepl,"$1"+index+"$2"));
    removebutton.style.visibility="visible";
  };
  tbody.insertBefore(copy,tbody.lastChild);
};

removeRowFromReferenceLookupWidget = function(input) {
    var row = input;
  while (row.nodeName != 'TR') row = row.parentNode;
  var tbody = row.parentNode;
  if (tbody.getElementsByTagName('tr').length > 2) {
    tbody.removeChild(row);
  } else {
    alert('You must have at least one reference');
  }
}