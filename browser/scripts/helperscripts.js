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

/* helper for the lookup window widgets, to add an additional
   row for placing a reference */
addRowToReferenceLookupWidget = function(input,maxrows) {
  var tbody = input;
  while (tbody.nodeName != 'TBODY') tbody = tbody.parentNode;
  /* count the number of RLW rows currently present */
  var trs = -1; /* start at -1, since one row is the add buttonr ow */
  for (var n=0; n < tbody.childNodes.length; n++) {
    if (tbody.childNodes[n].tagName == 'TR')
      trs++;      
  };
  if (trs == maxrows) {
    alert("Unable to add additional reference.  The number of references allowed for this field is " + maxrows);
    return;
  };
  /* lastchild is the row with the "add" button.
     the previousSibling is what we want to copy */
  var copy = tbody.lastChild.previousSibling.cloneNode(true);
  var key = input.getAttribute('id').replace(/^addbutton_/,'');
  var refinput = copy.getElementsByTagName('textarea')[0]; /* this is the ref text field*/
  var index = parseInt(refinput.id.replace(/^input(\d*)_.*$/,'$1')) + 1;
  refinput.value = '';
  refinput.id = 'input' + index + '_' + key;
  refinput.setAttribute('taid', 'inputta' + index + '_' + key);
/*  var ta = copy.getElementsByTagName('textarea')[0];
  ta.id = 'inputta' + index + '_' + key;
  ta.setAttribute('key', refinput.id);
  ta.name = ta.id;*/
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
    removebutton.style.display="inline";
  };
  tbody.insertBefore(copy,tbody.lastChild);
};

removeRowFromReferenceLookupWidget = function(input) {
    var row = input;
  while (row.nodeName != 'TR') row = row.parentNode;
  var tbody = row.parentNode;
  if (tbody.getElementsByTagName('TR').length > 2) {
    tbody.removeChild(row);
  } else {
    alert('You must have at least one reference');
  }
}
